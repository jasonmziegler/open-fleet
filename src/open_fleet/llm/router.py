# src/open_fleet/llm/router.py
"""LLM router with automatic fallback and per-provider validation retry.

Routing logic:
  1. Try LMStudioProvider first.
  2. LLMValidationError from the active provider → retry that same provider once.
     If the retry also fails, raise LLMValidationError to the caller.
  3. LLMTimeoutError or LLMProviderError from LM Studio → automatic Gemini fallback.
  4. Any error from Gemini (after optional validation retry) → raise to caller.

The router logs every run with the 5 required fields (FR19):
  provider, email_count, action_item_count, duration_ms, error

Slack notifications about LM Studio → Gemini fallover are delivered via an optional
async notify callback so this module stays free of any Slack imports.
"""
from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable

from open_fleet.exceptions import LLMProviderError, LLMTimeoutError, LLMValidationError
from open_fleet.llm.gemini import GeminiProvider
from open_fleet.llm.lmstudio import LMStudioProvider
from open_fleet.llm.schemas import ExtractionResult

logger = logging.getLogger("open_fleet.llm.router")

_NotifyFn = Callable[[str], Awaitable[None]]


class LLMRouter:
    """Routes extraction requests across LM Studio (primary) and Gemini (fallback).

    Args:
        lmstudio:       Configured LMStudioProvider instance.
        gemini:         Configured GeminiProvider instance.
        max_batch_size: Max emails per LLM call (default 10). Larger batches
                        are split and results merged. Keeps prompts within
                        local model context windows.
    """

    def __init__(
        self,
        lmstudio: LMStudioProvider,
        gemini: GeminiProvider,
        max_batch_size: int = 10,
    ) -> None:
        self._lmstudio = lmstudio
        self._gemini = gemini
        self._max_batch_size = max_batch_size

    async def run_extraction(
        self,
        email_batch: list[dict],
        timeframe: str = "last 24 hours",
        notify: _NotifyFn | None = None,
    ) -> ExtractionResult:
        """Extract action items, routing through providers with retry and fallback.

        When email_batch exceeds max_batch_size, emails are split into chunks
        and each chunk is extracted independently. Results are merged at the end.

        Args:
            email_batch: List of dicts with keys: subject, sender, timestamp, body.
            timeframe:   Human-readable timeframe string included in the prompt.
            notify:      Optional async callable invoked with a warning string when
                         LM Studio falls back to Gemini — use to send a Slack DM.

        Returns:
            Validated ExtractionResult.

        Raises:
            LLMValidationError: Active provider failed schema validation twice.
            LLMProviderError:   Active provider is unreachable or returned an error.
            LLMTimeoutError:    Active provider exceeded its timeout (LM Studio only).
        """
        chunks = [
            email_batch[i : i + self._max_batch_size]
            for i in range(0, len(email_batch), self._max_batch_size)
        ]
        if len(chunks) > 1:
            logger.info(
                "Splitting emails into batches",
                extra={"total_emails": len(email_batch), "batch_count": len(chunks)},
            )

        results: list[ExtractionResult] = []
        for idx, chunk in enumerate(chunks):
            start = time.monotonic()
            active_provider = "lmstudio"

            try:
                # ── Primary: LM Studio ──────────────────────────────────────
                try:
                    result = await self._try_with_retry(self._lmstudio, chunk, timeframe)
                    self._log_run(active_provider, chunk, result, start, error=None)
                    results.append(result)
                    continue
                except (LLMTimeoutError, LLMProviderError) as exc:
                    # Only notify on the first fallback to avoid spamming
                    if idx == 0:
                        logger.warning(
                            "LM Studio unavailable — falling back to Gemini",
                            extra={"provider": "lmstudio", "reason": str(exc)},
                        )
                        if notify is not None:
                            await notify(
                                "⚠️ LM Studio unavailable — falling back to Gemini for this run"
                            )

                # ── Fallback: Gemini ────────────────────────────────────────
                active_provider = "gemini"
                result = await self._try_with_retry(self._gemini, chunk, timeframe)
                self._log_run(active_provider, chunk, result, start, error=None)
                results.append(result)

            except Exception as exc:
                self._log_run(active_provider, chunk, None, start, error=exc)
                raise

        return self._merge_results(results, timeframe, len(email_batch))

    # ── Internal helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _merge_results(
        results: list[ExtractionResult],
        timeframe: str,
        total_emails: int,
    ) -> ExtractionResult:
        """Merge multiple batch results into a single ExtractionResult."""
        if len(results) == 1:
            return results[0]
        all_items = []
        for r in results:
            all_items.extend(r.action_items)
        return ExtractionResult(
            action_items=all_items,
            emails_scanned=total_emails,
            timeframe=timeframe,
        )

    @staticmethod
    async def _try_with_retry(provider, email_batch: list[dict], timeframe: str) -> ExtractionResult:
        """Call provider.extract(); on LLMValidationError retry exactly once.

        Any other exception (timeout, provider error) propagates immediately.
        If the retry also raises, that exception propagates.
        """
        try:
            return await provider.extract(email_batch, timeframe)
        except LLMValidationError as first_exc:
            logger.warning(
                "Validation error on first attempt — retrying same provider",
                extra={"error": str(first_exc)},
            )
            return await provider.extract(email_batch, timeframe)

    @staticmethod
    def _log_run(
        provider: str,
        email_batch: list[dict],
        result: ExtractionResult | None,
        start: float,
        error: Exception | None,
    ) -> None:
        duration_ms = int((time.monotonic() - start) * 1000)
        action_item_count = len(result.action_items) if result is not None else 0
        error_str = f"{type(error).__name__}: {error}" if error is not None else None
        log_fn = logger.error if error is not None else logger.info
        log_fn(
            "LLM router extraction %s" % ("failed" if error is not None else "complete"),
            extra={
                "provider": provider,
                "email_count": len(email_batch),
                "action_item_count": action_item_count,
                "duration_ms": duration_ms,
                "error": error_str,
            },
        )

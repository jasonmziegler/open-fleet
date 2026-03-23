# src/open_fleet/core/response.py
"""Response formatter — converts ExtractionResult into Slack-ready message strings.

No imports from slack_bolt, slack_sdk, or any Slack-specific module (NFR15, NFR16).
All inputs and outputs are plain Python types and Pydantic models only (NFR16).
"""
from __future__ import annotations

from datetime import datetime, timezone

from open_fleet.llm.schemas import ActionItem, ExtractionResult

_MAX_MSG_CHARS = 4_000

# Display groups rendered in priority order (bucket_index, header_text).
_GROUPS: list[tuple[int, str]] = [
    (0, "🔴 *Urgent*"),
    (1, "💬 *Needs Response*"),
    (2, "⏰ *Approaching Deadline*"),
    (3, "🟡 *This Week*"),
    (4, "🟢 *No Deadline*"),
]


def _assign_bucket(item: ActionItem) -> int:
    """Map one ActionItem to exactly one display-group bucket index."""
    if item.priority == "urgent":
        return 0
    if item.sentiment in ("frustrated", "escalated"):
        return 1
    if item.priority == "this_week" and item.deadline:
        return 2
    if item.priority == "this_week":
        return 3
    return 4  # no_deadline + neutral


def _display_name(sender: str) -> str:
    """Return display name from 'Name <email@domain>' or the raw sender string."""
    if "<" in sender:
        name = sender[: sender.index("<")].strip()
        if name:
            return name
        # No display name before angle bracket — extract the email address itself
        email = sender[sender.index("<") + 1 :].rstrip(">").strip()
        return email if email else sender
    return sender


def _format_timestamp(email_timestamp: str) -> str:
    """Format an ISO8601 UTC timestamp as 'Mon 01 Mar 09:00 UTC'."""
    try:
        ts = datetime.fromisoformat(email_timestamp).astimezone(timezone.utc)
        return ts.strftime("%a %d %b %H:%M UTC")
    except (ValueError, TypeError):
        return str(email_timestamp)


def _format_item(item: ActionItem) -> str:
    """Render a single ActionItem as a two-line string."""
    name = _display_name(item.sender)
    time_str = _format_timestamp(item.email_timestamp)
    sentiment_str = (
        f" | 💬 {item.sentiment}" if item.sentiment in ("frustrated", "escalated") else ""
    )
    context = item.context[:100]
    return f"• *{name}* — {time_str}{sentiment_str}\n  {context}"


def _assemble(chunks: list[str]) -> list[str]:
    """Join chunks into messages ≤ _MAX_MSG_CHARS, never splitting mid-chunk."""
    messages: list[str] = []
    current = ""
    for chunk in chunks:
        sep = "\n" if current else ""
        if current and len(current) + len(sep) + len(chunk) > _MAX_MSG_CHARS:
            messages.append(current)
            current = chunk
        else:
            current = current + sep + chunk
    if current:
        messages.append(current)
    return messages


class ResponseFormatter:
    """Formats an ExtractionResult into one or more Slack-ready message strings.

    Items are grouped by priority tier:
      🔴 Urgent → 💬 Needs Response → ⏰ Approaching Deadline → 🟡 This Week → 🟢 No Deadline

    Empty groups are omitted. Messages are split at 4,000-character boundaries
    without cutting any action item mid-entry (FR23).
    """

    @staticmethod
    def format(result: ExtractionResult) -> list[str]:
        """Convert an ExtractionResult into a list of Slack-ready strings.

        Args:
            result: Validated ExtractionResult from the LLM router.

        Returns:
            Non-empty list of strings; each string is ≤ 4,000 characters.
        """
        chunks: list[str] = []

        # ── Header ────────────────────────────────────────────────────────────
        count = result.emails_scanned
        email_word = "email" if count == 1 else "emails"
        chunks.append(
            f"📬 *Email Triage* — {result.timeframe} | {count} {email_word} scanned"
        )

        # ── Group items into buckets ──────────────────────────────────────────
        buckets: dict[int, list[ActionItem]] = {i: [] for i in range(5)}
        for item in result.action_items:
            buckets[_assign_bucket(item)].append(item)

        # ── Render each non-empty group ───────────────────────────────────────
        for bucket_idx, group_header in _GROUPS:
            items = buckets[bucket_idx]
            if not items:
                continue
            chunks.append(f"\n{group_header}")
            for item in items:
                chunks.append(_format_item(item))

        return _assemble(chunks)

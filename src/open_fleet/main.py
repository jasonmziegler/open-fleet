"""Entry point for the open-fleet agent.

Initialization order (architecture constraint):
  1. config.load()         — validates .env and token.json; raises ConfigError on failure
  2. logging_setup.configure() — attaches JSON handlers before any other module logs
  3. Build providers/clients with config-injected values
  4. Wire Orchestrator
  5. Register SlackHandler on AsyncApp
  6. Connect via Socket Mode and block
"""
from __future__ import annotations

import asyncio
import logging
import sys

from slack_bolt.async_app import AsyncApp

import open_fleet.config as config_module
import open_fleet.logging_setup as logging_setup
from open_fleet.adapters.slack.handler import SlackHandler, start as slack_start
from open_fleet.core.orchestrator import Orchestrator
from open_fleet.exceptions import ConfigError
from open_fleet.llm.gemini import GeminiProvider
from open_fleet.llm.lmstudio import LMStudioProvider
from open_fleet.llm.router import LLMRouter
from open_fleet.tools.gmail import GmailClient


async def _run() -> None:
    # ── 1. Load and validate configuration ──────────────────────────────────
    try:
        cfg = config_module.load()
    except ConfigError as exc:
        # Logging not yet configured — print directly so the message is visible.
        print(f"[open-fleet] Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)

    # ── 2. Configure structured logging ─────────────────────────────────────
    logging_setup.configure(log_dir=cfg.log_dir)
    logger = logging.getLogger("open_fleet.main")
    logger.info("open-fleet agent starting")

    # ── 3. Build components with injected config ─────────────────────────────
    gmail_client = GmailClient(token_path=cfg.gmail_token_path)
    lmstudio = LMStudioProvider(
        base_url=cfg.lm_studio_base_url,
        timeout_secs=cfg.lm_studio_timeout_secs,
    )
    gemini = GeminiProvider(api_key=cfg.gemini_api_key)
    router = LLMRouter(lmstudio=lmstudio, gemini=gemini)

    # ── 4. Wire orchestrator ─────────────────────────────────────────────────
    orchestrator = Orchestrator(gmail_client=gmail_client, llm_router=router)

    # ── 5. Register Slack handler ────────────────────────────────────────────
    app = AsyncApp(token=cfg.slack_bot_token)
    SlackHandler(app=app, orchestrator=orchestrator)

    # ── 6. Connect via Socket Mode and block ─────────────────────────────────
    logger.info("Connecting to Slack via Socket Mode")
    await slack_start(app=app, slack_app_token=cfg.slack_app_token)


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()

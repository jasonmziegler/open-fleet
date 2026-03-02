# src/open_fleet/llm/schemas.py
"""Pydantic v2 data models — the typed contract between the LLM layer and core layer.

These models are the single source of truth for what the LLM must produce.
Every LLM response is validated via ExtractionResult.model_validate() before
any downstream code touches the data.

Import rules (enforced by architecture):
  - This module may NOT import from adapters/, tools/, or core/.
  - It may be imported by any module in the project.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, field_validator


class ActionItem(BaseModel):
    """A single action item extracted from one or more emails."""

    description: str
    client: str
    sender: str
    email_timestamp: str
    deadline: str | None
    priority: Literal["urgent", "this_week", "no_deadline"]
    sentiment: Literal["neutral", "frustrated", "escalated"]
    context: str

    @field_validator("context")
    @classmethod
    def context_max_100_chars(cls, v: str) -> str:
        """Truncate context to 100 characters as required by FR21."""
        return v[:100]


class ExtractionResult(BaseModel):
    """The complete output of one LLM extraction run."""

    action_items: list[ActionItem]
    emails_scanned: int
    timeframe: str

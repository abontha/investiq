"""
Application-level configuration helpers.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List


def _parse_origins(raw: str | None) -> List[str]:
    """Parse a comma-separated CORS origin string."""
    if not raw:
        return ["http://localhost:5173", "http://127.0.0.1:5173"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@dataclass
class Settings:
    """Runtime configuration derived from environment variables."""

    lookback_years: int = int(os.getenv("FINRL_LOOKBACK_YEARS", "2"))
    test_window_days: int = int(os.getenv("FINRL_TEST_WINDOW_DAYS", "60"))
    training_timesteps: int = int(os.getenv("FINRL_TRAINING_TIMESTEPS", "10000"))
    cache_ttl_minutes: int = int(os.getenv("FINRL_CACHE_TTL_MINUTES", "60"))
    cors_origins: List[str] = field(
        default_factory=lambda: _parse_origins(os.getenv("FINRL_CORS_ORIGINS"))
    )


settings = Settings()


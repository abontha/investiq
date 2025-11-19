"""Railway/CLI entry point for launching the FastAPI service."""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    """Start uvicorn using the module path expected by FastAPI."""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
    )


if __name__ == "__main__":
    main()

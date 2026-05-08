"""
Entry point for the Telegram Cleanup API server.

Usage:
    python -m api.run
    # or
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 1
"""
from __future__ import annotations

import os

import uvicorn

from api.main import app  # noqa: F401

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1,
    )

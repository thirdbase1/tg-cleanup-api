"""
Telegram Cleanup API — A clean REST API for Telegram account cleanup.

Built on FastAPI with the telegram-cleanup SDK.
"""
from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import HealthResponse
from routers import auth_router, cleanup_router, analysis_router, export_router

# ─── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Telegram Cleanup API",
    description=(
        "A clean, professional REST API for Telegram account cleanup.\n\n"
        "## Features\n"
        "- **Secure Login** — Phone + Code + 2FA authentication flow\n"
        "- **Smart Analysis** — Scan chats, detect spam, estimate time\n"
        "- **Flexible Whitelist** — Keep important chats by username, link, or ID\n"
        "- **Full Cleanup** — Leave channels/groups, block bots, delete private chats\n"
        "- **Data Export** — Backup your chat data as JSON before deletion\n"
        "- **Progress Tracking** — Real-time cleanup progress monitoring\n"
        "- **Privacy First** — One-click logout wipes all session data\n\n"
        "## Workflow\n"
        "1. `POST /api/v1/auth/login/phone` — Send login code\n"
        "2. `POST /api/v1/auth/login/code` — Verify code (or 2FA)\n"
        "3. `POST /api/v1/analysis/whitelist` — Set whitelist (optional)\n"
        "4. `POST /api/v1/analysis/analyze` — Preview what will be cleaned\n"
        "5. `POST /api/v1/cleanup/start` — Start the cleanup\n"
        "6. `GET  /api/v1/cleanup/progress` — Track progress\n"
        "7. `GET  /api/v1/cleanup/result` — Get final results\n"
        "8. `POST /api/v1/auth/logout` — Wipe all data\n"
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────

API_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(analysis_router, prefix=API_PREFIX)
app.include_router(cleanup_router, prefix=API_PREFIX)
app.include_router(export_router, prefix=API_PREFIX)


# ─── Health Check ──────────────────────────────────────────────────────────────

@app.get("/", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return HealthResponse()


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    return HealthResponse()


# ─── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1,
    )

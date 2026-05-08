"""
Cleanup execution & progress tracking endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from models.schemas import (
    CleanupStartResponse,
    CleanupProgressResponse,
    CleanupResultResponse,
)
from services.cleanup_service import CleanupService

router = APIRouter(prefix="/cleanup", tags=["Cleanup"])


# ─── Start Cleanup ────────────────────────────────────────────────────────────

@router.post(
    "/start",
    response_model=CleanupStartResponse,
    summary="Start cleanup",
    description="Begin the cleanup process. Leaves channels/groups, blocks bots, deletes private chats.",
)
async def start_cleanup(
    session_id: str = Query(..., description="Session ID"),
):
    try:
        service = CleanupService(session_id)
        result = await service.start_cleanup()
        return CleanupStartResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Progress ─────────────────────────────────────────────────────────────────

@router.get(
    "/progress",
    response_model=CleanupProgressResponse,
    summary="Get cleanup progress",
    description="Returns current progress including processed count and recent logs.",
)
async def get_progress(
    session_id: str = Query(..., description="Session ID"),
):
    try:
        service = CleanupService(session_id)
        result = service.get_progress()
        return CleanupProgressResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── Result ───────────────────────────────────────────────────────────────────

@router.get(
    "/result",
    response_model=CleanupResultResponse,
    summary="Get cleanup result",
    description="Returns the final cleanup result. Only available after cleanup completes.",
)
async def get_result(
    session_id: str = Query(..., description="Session ID"),
):
    try:
        service = CleanupService(session_id)
        result = service.get_result()
        if result is None:
            raise HTTPException(
                status_code=202,
                detail="Cleanup is still in progress. Check /progress for updates.",
            )
        return CleanupResultResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

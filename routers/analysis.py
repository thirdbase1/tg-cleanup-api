"""
Account analysis & preview endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from models.schemas import (
    AccountAnalysisResponse,
    CleanupPreviewResponse,
    WhitelistRequest,
    WhitelistResponse,
)
from services.cleanup_service import CleanupService

router = APIRouter(prefix="/analysis", tags=["Analysis & Preview"])


# ─── Whitelist Management ─────────────────────────────────────────────────────

@router.get(
    "/whitelist",
    response_model=WhitelistResponse,
    summary="Get current whitelist",
)
async def get_whitelist(
    session_id: str = Query(..., description="Session ID"),
):
    try:
        service = CleanupService(session_id)
        items = service.get_whitelist()
        return WhitelistResponse(total_items=len(items), items=items)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/whitelist",
    response_model=WhitelistResponse,
    summary="Update whitelist",
    description="Add or replace whitelist items.",
)
async def update_whitelist(
    request: WhitelistRequest,
    session_id: str = Query(..., description="Session ID"),
):
    try:
        service = CleanupService(session_id)
        items = service.update_whitelist(request.items, request.mode)
        return WhitelistResponse(total_items=len(items), items=items)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── Account Analysis ─────────────────────────────────────────────────────────

@router.post(
    "/analyze",
    response_model=AccountAnalysisResponse,
    summary="Analyze account",
    description="Scan all chats, detect spam, and estimate cleanup time. Does NOT delete anything.",
)
async def analyze_account(
    session_id: str = Query(..., description="Session ID"),
):
    try:
        service = CleanupService(session_id)
        result = await service.analyze()
        return AccountAnalysisResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Cleanup Preview ──────────────────────────────────────────────────────────

@router.get(
    "/preview",
    response_model=CleanupPreviewResponse,
    summary="Get cleanup preview",
    description="Returns the last analysis result as a preview before running cleanup.",
)
async def get_preview(
    session_id: str = Query(..., description="Session ID"),
):
    try:
        service = CleanupService(session_id)
        result = await service.analyze()
        return CleanupPreviewResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

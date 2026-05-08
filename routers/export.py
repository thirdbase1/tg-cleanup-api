"""
Data export endpoints.
"""
from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from models.schemas import ExportResponse
from services.cleanup_service import CleanupService

router = APIRouter(prefix="/export", tags=["Export"])


# ─── Export Data ──────────────────────────────────────────────────────────────

@router.post(
    "/data",
    response_model=ExportResponse,
    summary="Export account data",
    description="Export all chat data to a JSON file before deletion.",
)
async def export_data(
    session_id: str = Query(..., description="Session ID"),
):
    try:
        service = CleanupService(session_id)
        result = await service.export_data()
        return ExportResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Download Export File ─────────────────────────────────────────────────────

@router.get(
    "/download",
    summary="Download exported file",
    description="Download the previously exported JSON file.",
)
async def download_export(
    session_id: str = Query(..., description="Session ID"),
):
    # Find the most recent export file for this session
    prefix = f"export_user_{session_id}_"
    export_dir = "."
    matching = [
        f for f in os.listdir(export_dir)
        if f.startswith(prefix) and f.endswith(".json")
    ]

    if not matching:
        raise HTTPException(status_code=404, detail="No export file found. Run /export/data first.")

    # Sort by modification time, newest first
    matching.sort(key=lambda f: os.path.getmtime(os.path.join(export_dir, f)), reverse=True)
    file_path = os.path.join(export_dir, matching[0])

    return FileResponse(
        file_path,
        media_type="application/json",
        filename=f"telegram_cleanup_export_{session_id}.json",
    )

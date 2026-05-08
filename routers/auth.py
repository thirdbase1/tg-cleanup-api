"""
Authentication & session management endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from models.schemas import (
    LoginPhoneRequest,
    LoginCodeRequest,
    Login2FARequest,
    LogoutResponse,
    SessionStatusResponse,
)
from services.session_manager import SessionManager

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _get_session_manager() -> SessionManager:
    return SessionManager.get_instance()


# ─── Login Step 1: Send Code ─────────────────────────────────────────────────

@router.post(
    "/login/phone",
    summary="Step 1: Send login code",
    description="Send a Telegram login code to the specified phone number.",
)
async def send_login_code(request: LoginPhoneRequest):
    try:
        manager = _get_session_manager()
        result = await manager.send_code(
            session_id=request.phone,  # Use phone as session key
            phone=request.phone,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── Login Step 2: Verify Code ───────────────────────────────────────────────

@router.post(
    "/login/code",
    summary="Step 2: Verify login code",
    description="Verify the code received via Telegram.",
)
async def verify_code(request: LoginCodeRequest):
    try:
        manager = _get_session_manager()
        result = await manager.verify_code(
            session_id=request.phone,
            code=request.code,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Login Step 3: Verify 2FA ────────────────────────────────────────────────

@router.post(
    "/login/2fa",
    summary="Step 3: Verify 2FA password",
    description="Provide your Two-Factor Authentication password.",
)
async def verify_2fa(request: Login2FARequest):
    try:
        manager = _get_session_manager()
        result = await manager.verify_2fa(
            session_id=request.phone,
            password=request.password,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Session Status ───────────────────────────────────────────────────────────

@router.get(
    "/status",
    response_model=SessionStatusResponse,
    summary="Check session status",
)
async def session_status(
    session_id: str = Query(..., description="Session ID (phone number)"),
):
    manager = _get_session_manager()
    session = manager.get(session_id)

    if not session:
        return SessionStatusResponse(authenticated=False)

    return SessionStatusResponse(
        authenticated=session.is_authenticated,
        phone=session.masked_phone(),
    )


# ─── Logout ───────────────────────────────────────────────────────────────────

@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Logout & wipe all data",
    description="Disconnect and permanently delete all session files.",
)
async def logout(
    session_id: str = Query(..., description="Session ID (phone number)"),
):
    try:
        manager = _get_session_manager()
        result = await manager.logout(session_id)
        return LogoutResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

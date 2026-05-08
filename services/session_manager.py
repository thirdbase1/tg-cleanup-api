"""
Manages user sessions, state, and TelegramCleaner instances.
"""
from __future__ import annotations

import asyncio
import os
import re
from typing import Any, Optional


from telethon import errors
from telethon.sessions import StringSession

from telegram_cleanup.config import load_config
from telegram_cleanup.sdk import TelegramCleaner


# ─── State constants ──────────────────────────────────────────────────────────

STATE_IDLE = "IDLE"
STATE_WAITING_PHONE = "WAITING_PHONE"
STATE_WAITING_CODE = "WAITING_CODE"
STATE_WAITING_2FA = "WAITING_2FA"
STATE_READY = "READY"
STATE_PREVIEWING = "PREVIEWING"
STATE_CLEANING = "CLEANING"


class UserSession:
    """Holds all state for a single user's cleanup session."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state: str = STATE_IDLE
        self.cleaner: Optional[TelegramCleaner] = None
        self.phone: Optional[str] = None
        self.phone_code_hash: Optional[str] = None
        self.whitelist: list[str] = []
        self.dialogs: list = []
        self.cleanup_task: Optional[asyncio.Task] = None
        self.log_buffer: list[str] = []
        self.cleanup_result: Optional[dict[str, Any]] = None
        self.cleanup_start_time: Optional[float] = None

    @property
    def is_authenticated(self) -> bool:
        if self.cleaner and self.cleaner.client.is_connected():
            # Use a simple flag — full check requires async
            return True
        return False

    def masked_phone(self) -> Optional[str]:
        if not self.phone:
            return None
        return self.phone[:4] + "****" + self.phone[-2:]


class SessionManager:
    """
    Singleton that tracks all active user sessions in memory.
    Each session is keyed by a unique session_id (e.g. API key or UUID).
    """

    _instance: Optional[SessionManager] = None

    def __init__(self) -> None:
        self._sessions: dict[str, UserSession] = {}

    @classmethod
    def get_instance(cls) -> SessionManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_or_create(self, session_id: str) -> UserSession:
        if session_id not in self._sessions:
            self._sessions[session_id] = UserSession(session_id)
        return self._sessions[session_id]

    def get(self, session_id: str) -> Optional[UserSession]:
        return self._sessions.get(session_id)

    def destroy(self, session_id: str) -> int:
        """Destroy a session and clean up files. Returns number of files removed."""
        session = self._sessions.pop(session_id, None)
        files_removed = 0
        if session and session.cleaner:
            # Remove session files
            prefix = f"user_{session_id}"
            files_to_remove = [
                f"sessions/{prefix}.session",
                f"sessions/{prefix}.session-journal",
                f"sessions/{prefix}_prefs.json",
                f"sessions/{prefix}_progress.json",
            ]
            for f in files_to_remove:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                        files_removed += 1
                    except OSError:
                        pass
        return files_removed

    # ── Convenience helpers ────────────────────────────────────────────────

    def _get_config(self) -> dict:
        return load_config()

    async def send_code(self, session_id: str, phone: str) -> dict:
        """Step 1: Send login code to the given phone number."""
        session = self.get_or_create(session_id)
        config = self._get_config()

        # Clean up old client if re-login
        if session.cleaner:
            try:
                await session.cleaner.client.disconnect()
            except Exception:
                pass

        session.phone = phone
        session.whitelist = []
        session.dialogs = []
        session.cleanup_result = None

        cleaner = TelegramCleaner(config, session_name=f"user_{session_id}")
        session.cleaner = cleaner

        await cleaner.client.connect()
        result = await cleaner.client.send_code_request(phone)
        session.phone_code_hash = result.phone_code_hash
        session.state = STATE_WAITING_CODE

        return {"status": "code_sent", "phone": phone}

    async def verify_code(self, session_id: str, code: str) -> dict:
        """Step 2: Verify the login code."""
        session = self.get(session_id)
        if not session or not session.cleaner:
            raise ValueError("No active session. Start with /login/phone first.")

        # Clean the code
        clean_code = re.sub(r"\D", "", code)
        if not clean_code or len(clean_code) < 5:
            raise ValueError("Invalid code format. Expected at least 5 digits.")

        try:
            await session.cleaner.client.sign_in(
                session.phone, clean_code, phone_code_hash=session.phone_code_hash
            )
            session.state = STATE_READY
            return {"status": "authenticated", "phone": session.masked_phone()}
        except errors.SessionPasswordNeededError:
            session.state = STATE_WAITING_2FA
            return {"status": "2fa_required", "message": "Please provide your 2FA password."}
        except Exception as e:
            raise ValueError(f"Code verification failed: {e}")

    async def verify_2fa(self, session_id: str, password: str) -> dict:
        """Step 3: Verify 2FA password."""
        session = self.get(session_id)
        if not session or not session.cleaner:
            raise ValueError("No active session.")

        try:
            await session.cleaner.client.sign_in(password=password)
            session.state = STATE_READY
            return {"status": "authenticated", "phone": session.masked_phone()}
        except Exception as e:
            raise ValueError(f"2FA verification failed: {e}")

    async def logout(self, session_id: str) -> dict:
        """Logout and wipe all session data."""
        session = self.get(session_id)
        files_removed = self.destroy(session_id)

        if session and session.cleaner:
            try:
                await session.cleaner.client.log_out()
            except Exception:
                try:
                    await session.cleaner.client.disconnect()
                except Exception:
                    pass

        return {
            "status": "logged_out",
            "message": "All session data has been permanently deleted.",
            "files_removed": files_removed,
        }

"""
High-level cleanup operations that wrap the TelegramCleaner SDK.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from typing import Any, AsyncGenerator, Optional


from services.session_manager import SessionManager, STATE_CLEANING, STATE_READY


class CleanupService:
    """Orchestrates the cleanup workflow for a given session."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.manager = SessionManager.get_instance()

    @property
    def session(self):
        return self.manager.get(self.session_id)

    # ── Whitelist ──────────────────────────────────────────────────────────

    def update_whitelist(self, items: list[str], mode: str = "add") -> list[str]:
        session = self.session
        if not session:
            raise ValueError("No active session.")

        if mode == "replace":
            session.whitelist = list(items)
        else:
            existing = set(session.whitelist)
            existing.update(items)
            session.whitelist = sorted(existing)

        # Persist to cleaner if available
        if session.cleaner:
            session.cleaner.prefs["kept_items"] = session.whitelist
            session.cleaner._save_data()

        return session.whitelist

    def get_whitelist(self) -> list[str]:
        session = self.session
        if not session:
            raise ValueError("No active session.")
        return session.whitelist

    # ── Analysis ───────────────────────────────────────────────────────────

    async def analyze(self) -> dict[str, Any]:
        """Scan the account and return analysis without deleting anything."""
        session = self.session
        if not session or not session.cleaner:
            raise ValueError("Not authenticated. Login first.")

        cleaner = session.cleaner

        # Prepare whitelist
        await cleaner._prepare_whitelist(set(session.whitelist))

        # Fetch dialogs
        dialogs = await cleaner._safe_iter_dialogs()
        session.dialogs = dialogs

        # Analyze activity
        activity = await cleaner.analyze_activity(dialogs)

        # Count items
        to_remove = []
        spam_bots = 0
        for d in dialogs:
            if not cleaner._is_whitelisted(d.entity):
                to_remove.append(d)
                if getattr(d.entity, "bot", False):
                    if cleaner.calculate_spam_score(d.entity) > 50:
                        spam_bots += 1

        total_whitelisted = len(dialogs) - len(to_remove)
        est_time = cleaner.estimate_duration(len(dialogs), total_whitelisted)

        session.state = "PREVIEWING"

        return {
            "total_chats": len(dialogs),
            "whitelisted": total_whitelisted,
            "to_remove": len(to_remove),
            "spam_bots_detected": spam_bots,
            "estimated_time": est_time,
            "activity": {
                "total": activity["total"],
                "inactive_7d": activity["inactive_7d"],
                "inactive_30d": activity["inactive_30d"],
                "inactive_90d": activity["inactive_90d"],
            },
            "whitelisted_breakdown": cleaner.whitelist_counts,
        }

    # ── Export ─────────────────────────────────────────────────────────────

    async def export_data(self) -> dict[str, Any]:
        """Export dialog data to a JSON file and return download info."""
        session = self.session
        if not session or not session.cleaner or not session.dialogs:
            raise ValueError("No data to export. Run analysis first.")

        export_file = await session.cleaner.export_data(session.dialogs)

        # Count records
        with open(export_file) as f:
            records = json.load(f)

        return {
            "status": "exported",
            "download_url": f"/api/v1/export/download?session_id={self.session_id}",
            "total_records": len(records),
            "file_path": export_file,
        }

    # ── Cleanup ────────────────────────────────────────────────────────────

    async def start_cleanup(self) -> dict[str, Any]:
        """Start the cleanup process in the background."""
        session = self.session
        if not session or not session.cleaner:
            raise ValueError("Not authenticated.")

        if session.state == STATE_CLEANING:
            raise ValueError("Cleanup already in progress.")

        session.state = STATE_CLEANING
        session.cleanup_start_time = time.time()
        session.log_buffer = []
        session.cleanup_result = None

        # Launch background task
        task = asyncio.create_task(self._run_cleanup())
        session.cleanup_task = task

        return {
            "status": "started",
            "message": "Cleanup has been initiated. Use the progress endpoint to track.",
            "session_id": self.session_id,
        }

    async def _run_cleanup(self) -> None:
        """Background cleanup task."""
        session = self.session
        if not session:
            return

        cleaner = session.cleaner

        async def progress_callback(msg: str):
            session.log_buffer.append(msg)
            if len(session.log_buffer) > 50:
                session.log_buffer = session.log_buffer[-50:]

        cleaner.progress_callback = progress_callback

        try:
            await cleaner.run_cleanup(set(session.whitelist))
            session.cleanup_result = {
                "status": "completed",
                "channels_left": cleaner.logs["channels_left"],
                "groups_left": cleaner.logs["groups_left"],
                "bots_blocked_deleted": cleaner.logs["bots_blocked_deleted"],
                "private_chats_deleted": cleaner.logs["private_chats_blocked_deleted"],
                "whitelisted_preserved": len(
                    [
                        n
                        for n in cleaner.logs["skipped_items"]
                        if n not in ("Saved Messages", "Telegram")
                        and "777000" not in n
                    ]
                ),
                "errors_count": len(cleaner.logs["errors"]),
                "remaining_chats": cleaner.logs["remaining_chats"],
                "duration_seconds": (
                    time.time() - session.cleanup_start_time
                    if session.cleanup_start_time
                    else None
                ),
            }
        except Exception as e:
            session.cleanup_result = {
                "status": "error",
                "error": str(e),
            }
        finally:
            session.state = STATE_READY

    def get_progress(self) -> dict[str, Any]:
        """Get current cleanup progress."""
        session = self.session
        if not session:
            raise ValueError("No active session.")

        logs = session.log_buffer[-10:] if session.log_buffer else []

        # Try to extract progress from logs
        processed = 0
        total = 0
        percentage = 0.0
        speed = 0

        for log in reversed(session.log_buffer):
            if "Progress:" in log:
                # Parse "📦 Progress: 45/100 (Concurrency: 2)"
                parts = log.split("Progress:")[-1].strip()
                nums = parts.split("/")
                if len(nums) >= 2:
                    processed = int(nums[0].strip())
                    total_str = nums[1].split(" ")[0]
                    total = int(total_str)
                break

        if total > 0:
            percentage = round((processed / total) * 100, 1)

        return {
            "processed": processed,
            "total": total,
            "percentage": percentage,
            "current_speed": speed,
            "recent_logs": logs,
        }

    def get_result(self) -> Optional[dict[str, Any]]:
        """Get the final cleanup result if available."""
        session = self.session
        if not session:
            raise ValueError("No active session.")
        return session.cleanup_result

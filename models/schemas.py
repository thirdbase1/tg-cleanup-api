"""
Pydantic models for request/response validation and API documentation.
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


# ─── Base ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "telegram-cleanup-api"
    version: str = "2.0.0"


# ─── Auth / Login ─────────────────────────────────────────────────────────────

class LoginPhoneRequest(BaseModel):
    phone: str = Field(
        ...,
        description="Phone number in international format",
        examples=["+1234567890"],
    )


class LoginCodeRequest(BaseModel):
    phone: str = Field(
        ...,
        description="Phone number (must match the one sent in step 1)",
        examples=["+1234567890"],
    )
    code: str = Field(
        ...,
        description="Login code received via Telegram",
        examples=["12345"],
    )


class Login2FARequest(BaseModel):
    phone: str = Field(
        ...,
        description="Phone number (must match the one sent in step 1)",
        examples=["+1234567890"],
    )
    password: str = Field(
        ...,
        description="Two-factor authentication password",
    )


class SessionStatusResponse(BaseModel):
    authenticated: bool = Field(
        ..., description="Whether the user is currently authenticated"
    )
    phone: Optional[str] = Field(
        None, description="Masked phone number if authenticated"
    )


# ─── Whitelist ────────────────────────────────────────────────────────────────

class WhitelistRequest(BaseModel):
    items: list[str] = Field(
        ...,
        description="Items to whitelist: usernames (@name), links (t.me/name), or IDs",
        examples=[["@MyFriend", "t.me/ImportantChannel", "1685547486"]],
    )
    mode: str = Field(
        default="add",
        description="'add' to append, 'replace' to overwrite",
        examples=["add", "replace"],
    )


class WhitelistResponse(BaseModel):
    total_items: int = Field(..., description="Total number of whitelisted items")
    items: list[str] = Field(..., description="Current whitelist items")


# ─── Analysis ─────────────────────────────────────────────────────────────────

class ActivityStats(BaseModel):
    total: int = Field(..., description="Total number of dialogs")
    inactive_7d: int = Field(..., description="Chats inactive for 7+ days")
    inactive_30d: int = Field(..., description="Chats inactive for 30+ days")
    inactive_90d: int = Field(..., description="Chats inactive for 90+ days")


class AccountAnalysisResponse(BaseModel):
    total_chats: int = Field(..., description="Total chats found")
    whitelisted: int = Field(..., description="Number of whitelisted chats")
    to_remove: int = Field(..., description="Number of chats to be removed")
    spam_bots_detected: int = Field(..., description="Number of suspected spam bots")
    estimated_time: str = Field(..., description="Estimated cleanup duration")
    activity: ActivityStats


class CleanupPreviewResponse(BaseModel):
    total_chats: int = Field(..., description="Total chats found")
    whitelisted: int = Field(..., description="Number of whitelisted chats")
    to_remove: int = Field(..., description="Number of chats to be removed")
    spam_bots_detected: int = Field(..., description="Number of suspected spam bots")
    estimated_time: str = Field(..., description="Estimated cleanup duration")
    activity: ActivityStats
    whitelisted_breakdown: dict = Field(
        ..., description="Breakdown of whitelisted items by type"
    )


# ─── Cleanup ──────────────────────────────────────────────────────────────────

class CleanupStartResponse(BaseModel):
    status: str = Field(..., description="Status of the cleanup request")
    message: str = Field(..., description="Human-readable message")
    session_id: str = Field(..., description="Session ID for tracking progress")


class CleanupProgressResponse(BaseModel):
    processed: int = Field(..., description="Number of chats processed so far")
    total: int = Field(..., description="Total chats to process")
    percentage: float = Field(..., description="Progress percentage")
    current_speed: int = Field(..., description="Current concurrency level")
    recent_logs: list[str] = Field(
        ..., description="Most recent log messages"
    )


class CleanupResultResponse(BaseModel):
    status: str = Field(..., description="Final status: completed | error")
    channels_left: int = Field(..., description="Number of channels left")
    groups_left: int = Field(..., description="Number of groups left")
    bots_blocked_deleted: int = Field(
        ..., description="Number of bots blocked and deleted"
    )
    private_chats_deleted: int = Field(
        ..., description="Number of private chats deleted"
    )
    whitelisted_preserved: int = Field(
        ..., description="Number of whitelisted items preserved"
    )
    errors_count: int = Field(..., description="Number of errors encountered")
    remaining_chats: int = Field(
        ..., description="Number of chats remaining after cleanup"
    )
    duration_seconds: Optional[float] = Field(
        None, description="Total cleanup duration in seconds"
    )


# ─── Export ───────────────────────────────────────────────────────────────────

class ExportResponse(BaseModel):
    status: str = Field(..., description="Export status")
    download_url: str = Field(..., description="URL to download the exported JSON file")
    total_records: int = Field(..., description="Number of records in the export")


# ─── Logout ───────────────────────────────────────────────────────────────────

class LogoutResponse(BaseModel):
    status: str = Field(..., description="Logout status")
    message: str = Field(..., description="Confirmation message")
    files_removed: int = Field(
        ..., description="Number of session files removed"
    )


# ─── Error ────────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Human-readable error description")

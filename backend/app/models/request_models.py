"""
Pydantic models for API request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., min_length=1, description="User message")
    use_scrape: bool = Field(default=False, description="Whether to scrape a URL for context")
    scrape_url: Optional[str] = Field(default=None, description="URL to scrape if use_scrape is true")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    reply: str = Field(..., description="AI assistant reply")
    session_expired: bool = Field(default=False, description="Whether the session had expired")


class ResetRequest(BaseModel):
    """Request model for session reset endpoint."""
    session_id: str = Field(..., description="Session identifier to reset")


class ResetResponse(BaseModel):
    """Response model for session reset endpoint."""
    message: str = Field(..., description="Confirmation message")
    session_id: str = Field(..., description="Session identifier that was reset")


class SessionHistoryResponse(BaseModel):
    """Response model for session history endpoint."""
    session_id: str = Field(..., description="Session identifier")
    history: list[dict] = Field(..., description="List of conversation messages")
    message_count: int = Field(..., description="Number of messages in history")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Health status")

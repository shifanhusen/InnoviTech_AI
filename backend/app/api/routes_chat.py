"""
Chat API endpoints for AI assistant interaction.
"""
from fastapi import APIRouter, HTTPException, Depends
from redis import Redis
from app.models.request_models import (
    ChatRequest, ChatResponse,
    ResetRequest, ResetResponse,
    SessionHistoryResponse
)
from app.services.memory_service import MemoryService
from app.services.ollama_service import OllamaService
from app.services.scrape_service import ScrapeService
from app.services.search_service import SearchService
from app.utils.prompt_builder import build_prompt
from app.core.redis_client import get_redis
from app.utils.logger import logger
import re

router = APIRouter(prefix="/api/llm", tags=["Chat"])

# Initialize services
ollama_service = OllamaService()
scrape_service = ScrapeService()
search_service = SearchService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, redis_client: Redis = Depends(get_redis)):
    """
    Main chat endpoint for AI assistant interaction.
    
    Args:
        request: Chat request containing session_id, message, and optional scraping parameters
        redis_client: Redis client dependency
    
    Returns:
        AI assistant reply with session expiration status
    """
    try:
        # Initialize memory service
        memory = MemoryService(redis_client)
        
        # Check if session existed before
        session_existed = memory.session_exists(request.session_id)
        
        # Get conversation history
        history = memory.get_history(request.session_id)
        
        # Auto-detect if web search is needed
        search_keywords = [
            'search', 'find', 'look up', 'lookup', 'google',
            'what is', 'who is', 'where is', 'when is', 'how is',
            'current', 'latest', 'recent', 'news', 'today', 'now',
            'price', 'weather', 'stock', 'trending', 'happening'
        ]
        needs_search = any(keyword in request.message.lower() for keyword in search_keywords)
        
        # Optional web search
        search_results = None
        if needs_search and not request.use_scrape:
            logger.info(f"🌐 Auto web search triggered for: {request.message}")
            results = search_service.search(request.message, num_results=5)
            if results:
                search_results = search_service.format_results_for_prompt(results)
                logger.info(f"📊 Formatted search results for AI context")
            else:
                logger.warning(f"⚠️ No search results found for: {request.message}")
        
        # Optional web scraping
        scraped_text = None
        if request.use_scrape and request.scrape_url:
            logger.info(f"Scraping requested for URL: {request.scrape_url}")
            scraped_text = scrape_service.scrape_website(request.scrape_url)
        
        # Build prompt with search results or scraped content
        additional_context = search_results or scraped_text
        prompt = build_prompt(
            history=history,
            user_message=request.message,
            scraped_text=additional_context
        )
        
        # Call Ollama
        try:
            assistant_reply = ollama_service.call_ollama(prompt)
        except Exception as e:
            logger.error(f"Ollama service error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"AI service unavailable: {str(e)}"
            )
        
        # Store messages in memory
        memory.append_message(request.session_id, "user", request.message)
        memory.append_message(request.session_id, "assistant", assistant_reply)
        
        # Determine if session expired
        session_expired = not session_existed and len(history) == 0
        
        return ChatResponse(
            reply=assistant_reply,
            session_expired=session_expired
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred"
        )


@router.post("/reset", response_model=ResetResponse)
async def reset_session(request: ResetRequest, redis_client: Redis = Depends(get_redis)):
    """
    Reset conversation history for a session.
    
    Args:
        request: Reset request containing session_id
        redis_client: Redis client dependency
    
    Returns:
        Confirmation message
    """
    try:
        memory = MemoryService(redis_client)
        memory.reset_session(request.session_id)
        
        return ResetResponse(
            message="Session reset successfully",
            session_id=request.session_id
        )
    except Exception as e:
        logger.error(f"Error resetting session: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to reset session"
        )


@router.get("/session/{session_id}", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str, redis_client: Redis = Depends(get_redis)):
    """
    Retrieve conversation history for debugging purposes.
    
    Args:
        session_id: Session identifier
        redis_client: Redis client dependency
    
    Returns:
        Session history with message count
    """
    try:
        memory = MemoryService(redis_client)
        history = memory.get_history(session_id)
        
        return SessionHistoryResponse(
            session_id=session_id,
            history=history,
            message_count=len(history)
        )
    except Exception as e:
        logger.error(f"Error retrieving session history: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve session history"
        )

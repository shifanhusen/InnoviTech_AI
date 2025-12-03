"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import routes_chat, routes_health
from app.core.config import settings
from app.core.redis_client import RedisClient
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting AI Assistant API")
    logger.info(f"Ollama URL: {settings.OLLAMA_BASE_URL}")
    logger.info(f"Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    logger.info(f"Session TTL: {settings.SESSION_TTL_SECONDS} seconds")
    
    # Initialize Redis connection
    try:
        RedisClient.get_client()
    except Exception as e:
        logger.error(f"Failed to connect to Redis on startup: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Assistant API")
    RedisClient.close()


# Create FastAPI app
app = FastAPI(
    title="AI Assistant API",
    description="FastAPI backend for AI assistant with LLaMA 3.1 via Ollama",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes_health.router)
app.include_router(routes_chat.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI Assistant API",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level="info"
    )

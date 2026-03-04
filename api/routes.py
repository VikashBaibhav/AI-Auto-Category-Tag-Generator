"""
API Routes — FastAPI endpoints for product categorization.
"""
import time

from fastapi import APIRouter, HTTPException

from models.product_schema import AnalyzeRequest, AnalyzeResponse, HealthResponse
from lib.ai_engine import GeminiEngine
from lib.database import save_record, get_history, clear_history
from lib.logger import logger


router = APIRouter(prefix="/api", tags=["AI Categorization"])

# Engine is initialized lazily on first request
_engine: GeminiEngine = None


def get_engine() -> GeminiEngine:
    """Lazy-initialize the Gemini engine."""
    global _engine
    if _engine is None:
        _engine = GeminiEngine()
    return _engine


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_product(request: AnalyzeRequest):
    """
    Analyze a product description and return:
    - Primary category (from predefined list)
    - Sub-category
    - 5-10 SEO tags
    - Sustainability filters
    - AI reasoning
    """
    start = time.time()
    try:
        engine = get_engine()
        metadata = engine.categorize_product(
            description=request.description,
            product_name=request.product_name,
        )

        # Store in database
        save_record(
            description=request.description,
            metadata=metadata,
            product_name=request.product_name,
        )

        elapsed_ms = round((time.time() - start) * 1000, 1)
        logger.info(f"Analysis completed in {elapsed_ms}ms")

        return AnalyzeResponse(
            success=True,
            product_name=request.product_name,
            metadata=metadata,
            processing_time_ms=elapsed_ms,
        )

    except ValueError as e:
        elapsed_ms = round((time.time() - start) * 1000, 1)
        logger.error(f"Validation error: {e}")
        return AnalyzeResponse(
            success=False,
            error=str(e),
            processing_time_ms=elapsed_ms,
        )
    except Exception as e:
        elapsed_ms = round((time.time() - start) * 1000, 1)
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_analysis_history(limit: int = 20):
    """Retrieve recent product analysis results."""
    return {"history": get_history(limit)}


@router.delete("/history")
async def clear_analysis_history():
    """Clear all stored analysis records."""
    count = clear_history()
    return {"message": f"Cleared {count} records", "deleted": count}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """API health check."""
    return HealthResponse()

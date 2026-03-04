from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ProductMetadata(BaseModel):
    """AI-generated product categorization result."""
    primary_category: str = Field(..., description="Primary category from predefined list")
    sub_category: str = Field(..., description="More specific sub-category")
    seo_tags: List[str] = Field(..., description="5-10 SEO-optimized tags")
    sustainability_filters: List[str] = Field(..., description="Sustainability attributes like plastic-free, vegan, etc.")
    ai_reasoning: str = Field(..., description="Brief explanation of why these categories/tags were chosen")


class AnalyzeRequest(BaseModel):
    """Request body for the /api/analyze endpoint."""
    description: str = Field(..., min_length=10, max_length=5000, description="Product description to analyze")
    product_name: Optional[str] = Field(None, description="Optional product name for better accuracy")


class AnalyzeResponse(BaseModel):
    """Response body from the /api/analyze endpoint."""
    success: bool
    product_name: Optional[str] = None
    metadata: Optional[ProductMetadata] = None
    error: Optional[str] = None
    processing_time_ms: float = 0


class ProductRecord(BaseModel):
    """A stored product analysis record."""
    id: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    product_name: Optional[str] = None
    description: str
    metadata: ProductMetadata


class HealthResponse(BaseModel):
    """API health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    ai_model: str = "gemini-2.0-flash"
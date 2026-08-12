from pydantic import BaseModel, Field
from typing import Optional

class ForexAnalysis(BaseModel):
    """Structured response schema for forex analysis"""
    
    summary: str = Field(
        description="One line summary of the analysis"
    )
    current_price: Optional[float] = Field(
        default=None,
        description="Current price of the currency pair if available"
    )
    currency_pair: Optional[str] = Field(
        default=None,
        description="The currency pair being analyzed e.g. EUR/USD"
    )
    sentiment: Optional[str] = Field(
        default=None,
        description="Market sentiment: bullish, bearish, or neutral"
    )
    sentiment_score: Optional[float] = Field(
        default=None,
        description="Sentiment score between 0 and 1"
    )
    key_points: list[str] = Field(
        default=[],
        description="List of key analysis points, max 5 bullet points"
    )
    risk_note: Optional[str] = Field(
        default=None,
        description="Risk consideration based on user's risk tolerance"
    )
    disclaimer: str = Field(
        default="Not financial advice.",
        description="Standard disclaimer"
    )

from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    """Structured plan controlling web, news, and image research."""

    web: bool = Field(
        default=True,
        description="Whether Google web search should run.",
    )
    news: bool = Field(
        default=False,
        description="Whether Google News search should run.",
    )
    images: bool = Field(
        default=False,
        description="Whether Google Images search should run.",
    )

    web_query: str = Field(
        default="",
        description="One focused query for Google web search.",
    )
    news_query: str = Field(
        default="",
        description="One focused query for Google News search.",
    )
    image_query: str = Field(
        default="",
        description="One focused query for Google Images search.",
    )

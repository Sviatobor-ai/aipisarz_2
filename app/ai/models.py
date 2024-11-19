"""
File contains different models
"""

from pydantic import BaseModel, ConfigDict, Field


class TopicsKeywordsResponse(BaseModel):
    """
    This is response format of OpenAI.GPT for the fetching keywords and ceo optimized
    keywords from the given topic by user.
    """

    model_config = ConfigDict(title="topics_keys_words_and_ceo_keywords")

    topic: str = Field(description="Given topic by user")

    seo_keywords: list[str] = Field(
        description="List of SEO optimized keywords from the topic"
    )

    error: str | None = Field(
        description="Error message for example when the input(topic) is strange"
    )

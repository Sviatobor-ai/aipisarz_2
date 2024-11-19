from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.ai.assistants import OpenAIAssistant
from app.ai.models import TopicsKeywordsResponse
from app.core.config import settings
from app.models import GenerateArticleRequestModel

router = APIRouter()

assistant = OpenAIAssistant(token=settings.OPENAI_TOKEN)


@router.get("/get-keywords")
async def get_keywords(topic: str) -> TopicsKeywordsResponse:
    """
    Endpoint that is responsible for fetching contextual keywords from the given topic.
    If the topic is some non-sense, then the response field  `error` will not be empty
    and contain error message from the assistant.
    """
    return await assistant.fetch_topics_keywords(
        topic, assistant_id=settings.KEYWORDS_ASSISTANT_ID
    )


@router.post("/generate-article", response_class=StreamingResponse)
async def generate_article(body: GenerateArticleRequestModel) -> StreamingResponse:
    """
    Endpoint that is responsible for generating an article of the given topic and
    keywords which must exist in the generated article.
    The response is in stream format.
    """

    try:
        article_generator = assistant.generate_article(
            body.topic,
            body.keywords,
            assistant_id=settings.ARTICLE_GENERATOR_ASSISTANT_ID,
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred! :(",
        ) from error

    return StreamingResponse(article_generator, media_type="text/plain")

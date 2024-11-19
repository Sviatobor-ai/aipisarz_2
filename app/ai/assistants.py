"""
File contains different wrappers for assistants
"""

from collections.abc import AsyncGenerator
from typing import Any, cast

from openai import AsyncOpenAI
from openai.types.beta.assistant_stream_event import (
    ThreadMessageDelta,
    ThreadRunCreated,
    ThreadRunInProgress,
    ThreadRunQueued,
)
from openai.types.beta.threads.message import Message
from openai.types.beta.threads.text_content_block import TextContentBlock
from openai.types.beta.threads.text_delta_block import TextDeltaBlock
from openai.types.shared_params import ResponseFormatJSONSchema

from .models import TopicsKeywordsResponse
from .utils import OpenAISchemaGenerator


class OpenAIAssistant:
    MODEL: str = "gpt-4o-2024-08-06"

    def __init__(self, token: str) -> None:
        self._open_ai = AsyncOpenAI(api_key=token)

    async def fetch_topics_keywords(
        self, topic: str, assistant_id: str
    ) -> TopicsKeywordsResponse:
        response_format = cast(
            ResponseFormatJSONSchema,
            TopicsKeywordsResponse.model_json_schema(
                schema_generator=OpenAISchemaGenerator
            ),
        )
        thread = await self._open_ai.beta.threads.create(
            messages=[{"role": "user", "content": topic}]
        )
        response = await self._open_ai.beta.threads.runs.create_and_poll(
            model=self.MODEL,
            thread_id=thread.id,
            assistant_id=assistant_id,
            response_format=response_format,
        )

        if response.status == "completed":
            messages = await self._open_ai.beta.threads.messages.list(
                thread_id=thread.id
            )
            message: Message = messages.data[0]
            text_block: TextContentBlock | Any = message.content[0]
            assert isinstance(
                text_block, TextContentBlock
            ), "Unexpected error. Must be TextContentBlock"
            return TopicsKeywordsResponse.model_validate_json(text_block.text.value)

        else:
            raise RuntimeError(
                f"Unexpected response status from the assistant: {response.status}"
            )

    async def generate_article(
        self, topic: str, keywords: list[str], assistant_id: str
    ) -> AsyncGenerator[str, None]:
        wrapped_keywords = [f'"{keyword}"' for keyword in keywords]
        thread = await self._open_ai.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"topic: {topic};" f" keywords: {', '.join(wrapped_keywords)}"
                    ),
                }
            ]
        )
        events = await self._open_ai.beta.threads.runs.create(
            thread_id=thread.id, assistant_id=assistant_id, stream=True
        )

        async for e in events:
            if isinstance(e, ThreadRunCreated):
                print("ThreadRunCreated")
            elif isinstance(e, ThreadRunQueued):
                print("ThreadRunQueued")
            elif isinstance(e, ThreadRunInProgress):
                print("ThreadRunInProgress")
            elif isinstance(e, ThreadMessageDelta):
                deltas: list[TextDeltaBlock] = cast(
                    list[TextDeltaBlock], e.data.delta.content
                )

                yield str(deltas[0].text.value)  # type: ignore[union-attr]
            else:
                print(e)

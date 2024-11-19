"""
File contains different utils
"""

from typing import Any, Literal

from pydantic.json_schema import GenerateJsonSchema


class OpenAISchemaGenerator(GenerateJsonSchema):
    def generate(
        self,
        schema: Any,
        mode: Literal["validation"] | Literal["serialization"] = "validation",
    ) -> dict[str, Any]:
        json_schema = super().generate(schema, mode)
        json_schema["additionalProperties"] = False
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "assistant_response",
                "strict": True,
                "schema": json_schema,
            },
        }

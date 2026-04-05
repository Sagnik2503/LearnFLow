from openai import OpenAI
from pydantic import BaseModel
import os
import json


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"


def _get_openrouter_client() -> OpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set in environment")
    return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)


def call_openrouter(
    messages: list[dict],
    response_model: type[BaseModel] | None = None,
) -> BaseModel | str:
    client = _get_openrouter_client()

    response = client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=messages,
        extra_body={"reasoning": {"enabled": True}},
    )

    content = response.choices[0].message.content

    if response_model is not None:
        import re

        json_match = re.search(r"```(?:json)?\s*\n(.*?)\n```", content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError(f"No JSON object found in response: {content[:200]}")
            json_str = content[start:end]

        parsed = json.loads(json_str)

        normalized = {}
        for key, value in parsed.items():
            normalized[key.lower().replace(" ", "_").replace("-", "_")] = value

        if "feedbacks" not in normalized and "feedback" in normalized:
            normalized["feedbacks"] = normalized.pop("feedback")
        if "approved" not in normalized:
            for k in ("is_approved", "isapproved", "approve"):
                if k in normalized:
                    normalized["approved"] = normalized.pop(k)
                    break

        if "feedbacks" in normalized and isinstance(normalized["feedbacks"], list):
            normalized_feedbacks = []
            for fb in normalized["feedbacks"]:
                if isinstance(fb, dict):
                    norm_fb = {}
                    for k, v in fb.items():
                        norm_fb[k.lower().replace(" ", "_").replace("-", "_")] = v
                    if "section" not in norm_fb:
                        for k in ("heading", "area", "part"):
                            if k in norm_fb:
                                norm_fb["section"] = norm_fb.pop(k)
                                break
                    normalized_feedbacks.append(norm_fb)
                else:
                    normalized_feedbacks.append(fb)
            normalized["feedbacks"] = normalized_feedbacks

        clean_json = json.dumps(normalized)

        try:
            return response_model.model_validate_json(clean_json)
        except Exception as e:
            print(f"❌ Validation error. Raw content:\n{content[:800]}")
            print(f"Extracted JSON:\n{json_str[:800]}")
            print(f"Normalized JSON:\n{clean_json[:800]}")
            raise

    return content

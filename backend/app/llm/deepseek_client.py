from __future__ import annotations

import json

from openai import OpenAI
from openai import APIConnectionError, APIStatusError
from pydantic import BaseModel

from app.config import settings
from app.llm.base_client import BaseLLMClient
from app.utils.exceptions import LLMInvalidJSONError
from app.utils.json_utils import parse_json_model


class DeepSeekClient(BaseLLMClient):
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model_name: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        self.api_key = api_key or settings.deepseek_api_key
        self.base_url = base_url or settings.deepseek_base_url
        self.model_name = model_name or settings.deepseek_model
        self.timeout = timeout or settings.llm_timeout
        self.max_retries = max_retries if max_retries is not None else settings.llm_max_retries
        self.repair_retries = settings.llm_repair_retries

        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY 未配置。")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)

    def invoke_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
    ) -> BaseModel:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        last_error: Exception | None = None

        for _ in range(self.max_retries + 1):
            content = ""
            try:
                response = self._create_json_completion(messages)
                content = response.choices[0].message.content or ""
                return parse_json_model(content, response_model)
            except LLMInvalidJSONError as exc:
                last_error = exc
                repaired = self._repair_json_content(
                    invalid_content=content,
                    response_model=response_model,
                    original_system_prompt=system_prompt,
                )
                if repaired is not None:
                    return repaired

                messages.extend(
                    [
                        {"role": "assistant", "content": content},
                        {
                            "role": "user",
                            "content": (
                                "你的上一轮输出不是合法 JSON。"
                                "请严格只返回一个 JSON 对象，"
                                "不要包含解释、注释、Markdown 代码块，"
                                "并确保所有字符串正确转义。"
                            ),
                        },
                    ]
                )
            except APIConnectionError as exc:
                raise RuntimeError("无法连接到 DeepSeek API，请检查网络连通性或代理设置。") from exc
            except APIStatusError as exc:
                if exc.status_code == 402:
                    raise RuntimeError("DeepSeek API 调用失败：账户余额不足，请充值或更换可用的 API Key。") from exc
                raise RuntimeError(f"DeepSeek API 调用失败：HTTP {exc.status_code}。") from exc
            except Exception as exc:  # noqa: BLE001
                last_error = exc

        raise last_error or RuntimeError("调用 DeepSeek 失败。")

    def _create_json_completion(self, messages: list[dict[str, str]]):
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"},
        )

    def _repair_json_content(
        self,
        *,
        invalid_content: str,
        response_model: type[BaseModel],
        original_system_prompt: str,
    ) -> BaseModel | None:
        if not invalid_content.strip():
            return None

        repair_system_prompt = (
            "You repair malformed JSON responses. "
            "Return exactly one valid JSON object and nothing else. "
            "Preserve the original meaning, repair escaping, commas, quotes, and missing braces. "
            "Do not invent new fields outside the schema."
        )
        schema = json.dumps(response_model.model_json_schema(), ensure_ascii=False)
        repair_user_prompt = (
            "The following model output should conform to the target JSON schema but is invalid.\n"
            "Fix it into valid JSON that matches the schema.\n\n"
            f"Original system prompt summary:\n{original_system_prompt[:1200]}\n\n"
            f"Target schema:\n{schema}\n\n"
            f"Invalid JSON candidate:\n{invalid_content}"
        )

        for _ in range(self.repair_retries):
            try:
                response = self._create_json_completion(
                    [
                        {"role": "system", "content": repair_system_prompt},
                        {"role": "user", "content": repair_user_prompt},
                    ]
                )
                repaired_content = response.choices[0].message.content or ""
                return parse_json_model(repaired_content, response_model)
            except (LLMInvalidJSONError, APIConnectionError, APIStatusError):
                continue

        return None

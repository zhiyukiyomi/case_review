from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseLLMClient(ABC):
    @abstractmethod
    def invoke_json(self, *, system_prompt: str, user_prompt: str, response_model: type[BaseModel]) -> BaseModel:
        raise NotImplementedError


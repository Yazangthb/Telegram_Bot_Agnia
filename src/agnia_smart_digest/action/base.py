from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)


class Action(ABC, Generic[TInput, TOutput]):
    def __init__(self, action_name: str):
        self.action_name = action_name

    @abstractmethod
    async def execute(self, input_data: TInput) -> TOutput:
        pass

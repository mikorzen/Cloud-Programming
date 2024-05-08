import abc
from enum import IntEnum
from typing import Any

from pydantic import BaseModel, computed_field
from pydantic.dataclasses import dataclass

__all__ = [
    "Square",
    "ResponseType",
    "Response",
    "GameFullError",
    "IllegalMoveError",
    "GameOver",
]


class Square(IntEnum):
    EMPTY = 0
    X = 1
    O = 2  # noqa: E741


class ResponseType(IntEnum):
    ERROR = 1
    GAME_OVER = 2
    PLAYERS = 3
    STATE = 4


class Response(BaseModel, abc.ABC):
    @property
    @abc.abstractmethod
    def type(self: "Response") -> ResponseType: ...

    def json(self: "Response") -> dict[str, Any]:
        return self.model_dump()


class ErrorResponse(Response):
    type: ResponseType = ResponseType.ERROR
    error: str


class GameOverResponse(Response):
    type: ResponseType = ResponseType.GAME_OVER
    winner: Square | None

    @computed_field
    @property
    def draw(self: "GameOverResponse") -> bool:
        return self.winner is None


class PlayersResponse(Response):
    type: ResponseType = ResponseType.PLAYERS
    player: Square
    opponent: str | None


class StateResponse(Response):
    type: ResponseType = ResponseType.STATE
    turn: Square
    board: list[Square]


@dataclass
class GameError(Exception, abc.ABC):
    @property
    @abc.abstractmethod
    def response(self: "GameError") -> ErrorResponse: ...


class GameFullError(GameError):
    response: ErrorResponse = ErrorResponse(error="Game is full")


class IllegalMoveError(GameError):
    response: ErrorResponse = ErrorResponse(error="Illegal move")


class GameOver(Exception):  # noqa: N818
    pass

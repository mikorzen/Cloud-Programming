from enum import Enum
from typing import Any

from pydantic.dataclasses import dataclass

__all__ = [
    "Cell",
    "ResponseType",
    "Response",
    "GameFullError",
    "IllegalMoveError",
    "GameOver",
    "Draw",
]


class Cell(Enum):
    X = True
    O = False  # noqa: E741
    EMPTY = None


class ResponseType(str, Enum):
    ERROR = "error"
    GAME_OVER = "game_over"
    USERNAMES = "usernames"
    STATE_CHANGE = "state_change"


@dataclass
class Response:
    type: ResponseType
    message: str | dict[str, Any]

    def json(self: "Response") -> dict[str, Any]:
        return {"type": self.type, "message": self.message}


@dataclass
class BaseGameError(Exception):
    response: Response


class GameError(BaseGameError):
    def __init__(self: "GameError", message: dict[str, Any]) -> None:
        response = Response(
            type=ResponseType.ERROR,
            message=message,
        )
        super().__init__(response)


class GameFullError(GameError):
    def __init__(self: "GameFullError") -> None:
        message = {"error": "Game is full"}
        super().__init__(message)


class IllegalMoveError(GameError):
    def __init__(self: "IllegalMoveError") -> None:
        message = {"error": "Illegal move"}
        super().__init__(message)


class GameOver(GameError):  # noqa: N818
    def __init__(self: "GameOver", winner: Cell | None) -> None:
        message = {"error": "Game over", "winner": winner}
        super().__init__(message)


class Draw(GameOver):
    def __init__(self: "Draw") -> None:
        super().__init__(None)

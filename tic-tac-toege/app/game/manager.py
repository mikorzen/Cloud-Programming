from typing import Any

from fastapi import WebSocket
from game.state import GameState
from models import (
    Draw,
    GameOver,
    IllegalMoveError,
    Response,
    ResponseType,
)

type Player = dict[str, Any]
type Players = tuple[Player, Player]


class GameManager:
    def __init__(self: "GameManager") -> None:
        self._game = GameState()
        self._player_x: Player = {"symbol": "X"}
        self._player_o: Player = {"symbol": "O"}
        self._players: Players = (self._player_x, self._player_o)

    @property
    def game(self: "GameManager") -> GameState:
        return self._game

    @property
    def player_x(self: "GameManager") -> Player:
        return self._player_x

    @property
    def player_o(self: "GameManager") -> Player:
        return self._player_o

    @property
    def players(self: "GameManager") -> Players:
        return self._players

    async def connect(self: "GameManager", websocket: WebSocket) -> None:
        await websocket.accept()

        for player in self.players:
            if not player.get("websocket"):
                player.update({"websocket": websocket})
                break

    async def assign_username(
        self: "GameManager",
        websocket: WebSocket,
        username: str,
    ) -> None:
        for player in self.players:
            if player.get("websocket") == websocket:
                player.update({"username": username})

        message = {
            "player_x": self.player_x.get("username"),
            "player_o": self.player_o.get("username"),
        }

        await websocket.send_json(
            Response(type=ResponseType.USERNAMES, message=message).json(),
        )

    async def run_game(self: "GameManager", websocket: WebSocket) -> None:
        while True:
            message = await websocket.receive_json()

            if username := message.get("username"):
                await self.assign_username(websocket, username)
                continue

            move = message.get("position")
            try:
                self.game.make_move(move)
            except IllegalMoveError as e:
                await websocket.send_json(e.response.json())
                continue
            except (Draw, GameOver) as e:
                await websocket.send_json(e.response.json())
                break

            await self.broadcast_state(websocket)

    async def broadcast_state(self: "GameManager", websocket: WebSocket) -> None:
        message = {
            "turn": self.game.turn,
            "board": self.game.board,
        }
        for player in self.players:
            message["player"] = player["symbol"]
            await websocket.send_json(
                Response(
                    type=ResponseType.STATE_CHANGE,
                    message=message,
                ).json(),
            )

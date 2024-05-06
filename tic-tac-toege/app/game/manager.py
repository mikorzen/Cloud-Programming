from typing import Any

from fastapi import WebSocket
from game.state import GameState
from models import (
    GameOver,
    GameOverResponse,
    IllegalMoveError,
    PlayersResponse,
    Response,
    ResponseType,
    Square,
    StateResponse,
)

type Message = dict[str, Any]
type Player = dict[str, Any]
type Players = tuple[Player, Player]


class GameManager:
    def __init__(self: "GameManager") -> None:
        self._game = GameState()
        self._player1: Player = {"player": Square.X}
        self._player2: Player = {"player": Square.O}
        self._players: Players = (self._player1, self._player2)

    @property
    def game(self: "GameManager") -> GameState:
        return self._game

    @property
    def player1(self: "GameManager") -> Player:
        return self._player1

    @property
    def player2(self: "GameManager") -> Player:
        return self._player2

    @property
    def players(self: "GameManager") -> Players:
        return self._players

    async def connect(self: "GameManager", websocket: WebSocket) -> None:
        await websocket.accept()

        for player in self.players:
            if not player.get("websocket"):
                player.update({"websocket": websocket})
                break

    async def assign_player(
        self: "GameManager",
        username: str,
    ) -> None:
        if not self.player1.get("username"):
            self.player1.update({"username": username})
            await self.broadcast(ResponseType.PLAYERS)
            await self.broadcast(ResponseType.STATE)
            return

        player1_username = self.player1.get("username")
        self.player1.update({"opponent": username})
        self.player2.update({"username": username, "opponent": player1_username})

        await self.broadcast(ResponseType.PLAYERS)
        await self.broadcast(ResponseType.STATE)

    async def run_game(self: "GameManager", websocket: WebSocket) -> None:
        while True:
            message = await websocket.receive_json()

            if username := message.get("username"):
                await self.assign_player(username)
                continue

            move = message.get("position")
            try:
                self.game.make_move(int(move))
            except IllegalMoveError as e:
                await websocket.send_json(e.response.json())
                continue
            except GameOver:
                await self.broadcast(ResponseType.GAME_OVER)
                break

            await self.broadcast(ResponseType.STATE)

    async def broadcast(self: "GameManager", response_type: ResponseType) -> None:
        for player in self.players:
            websocket = player.get("websocket")
            if not websocket:
                continue
            response: Response
            match response_type:
                case ResponseType.GAME_OVER:
                    response = GameOverResponse(
                        winner=self.game.winner,
                    )
                case ResponseType.PLAYERS:
                    response = PlayersResponse(
                        player=player["player"],
                        opponent=player.get("opponent"),
                    )
                case ResponseType.STATE:
                    response = StateResponse(
                        turn=self.game.turn,
                        board=self.game.board,
                    )
            await websocket.send_json(response.json())

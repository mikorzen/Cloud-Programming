from typing import Any

from fastapi import WebSocket
from logic.tictactoe import Draw, TicTacToe

type Player = dict[str, Any]

VALID_POSITIONS = [*range(9)]


class GameFullError(Exception):
    def __init__(self: "GameFullError") -> None:
        super().__init__("Game is full")


class InvalidMoveError(Exception):
    def __init__(self: "InvalidMoveError") -> None:
        super().__init__("Invalid move")


class GameOver(Exception):  # noqa: N818
    def __init__(self: "GameOver") -> None:
        super().__init__("Game Over")


class GameManager:
    def __init__(self: "GameManager") -> None:
        self._game = TicTacToe()
        self._player_x: Player = {}
        self._player_o: Player = {}

    @property
    def game(self: "GameManager") -> TicTacToe:
        return self._game

    @property
    def player_x(self: "GameManager") -> Player:
        return self._player_x

    @property
    def player_o(self: "GameManager") -> Player:
        return self._player_o

    def assign_username(
        self: "GameManager",
        websocket: WebSocket,
        username: str,
    ) -> None:
        if websocket == self.player_x["websocket"]:
            self.player_x.update({"username": username})
        elif websocket == self.player_o["websocket"]:
            self.player_o.update({"username": username})

    def get_winner(self: "GameManager") -> str | None:
        if self.game.winner == "X":
            return self.player_x.get("username")
        if self.game.winner == "O":
            return self.player_o.get("username")
        return None

    async def connect(self: "GameManager", websocket: WebSocket) -> None:
        await websocket.accept()
        if not self.player_x.get("websocket"):
            self.player_x.update({"websocket": websocket})
        elif not self.player_o.get("websocket"):
            self.player_o.update({"websocket": websocket})
        else:
            raise GameFullError

    async def run_game(self: "GameManager", websocket: WebSocket) -> None:
        while True:
            message = await websocket.receive_json()
            if "username" in message and (username := message["username"]):
                self.assign_username(websocket, username)
                await self.broadcast()
                continue
            if (
                "position" not in message
                or (move := int(message["position"])) not in VALID_POSITIONS
            ):
                raise InvalidMoveError
            try:
                if self.game.make_move(move):
                    await self.broadcast()
                elif self.game.winner:
                    await self.broadcast()
                    raise GameOver
                else:
                    raise InvalidMoveError
            except Draw:
                await self.broadcast(draw=True)
                raise GameOver from Draw

    async def broadcast(self: "GameManager", draw: bool = False) -> None:  # noqa: FBT001, FBT002
        message = {
            "turn": self.game.turn,
            "board": self.game.board,
            "winner": draw or self.get_winner(),
        }
        if websocket := self.player_x.get("websocket"):
            message.update({"player": "X"})
            if opponent := self.player_o.get("username"):
                message.update({"opponent": opponent})
            await websocket.send_json(message)

        if websocket := self.player_o.get("websocket"):
            message.update({"player": "O", "opponent": self.player_x["username"]})
            await websocket.send_json(message)

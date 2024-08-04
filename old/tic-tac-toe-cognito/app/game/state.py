from itertools import cycle
from typing import Final

from models import GameOver, IllegalMoveError, Square

# fmt: off
WINNING_COMBINATIONS: Final = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
    (0, 4, 8), (2, 4, 6),             # Diagonals
)  # fmt: on
VALID_POSITIONS: Final = set(range(9))

class GameState:
    def __init__(self: "GameState") -> None:
        self._board = [Square.EMPTY for _ in range(9)]
        self._turn_cycle = cycle([Square.X, Square.O])
        self._turn = next(self._turn_cycle)
        self._winner = None

    @property
    def board(self: "GameState") -> list[Square]:
        return self._board

    @property
    def turn(self: "GameState") -> Square:
        return self._turn

    @property
    def winner(self: "GameState") -> Square | None:
        return self._winner

    @turn.setter
    def turn(self: "GameState", turn: Square) -> None:
        self._turn = turn

    @winner.setter
    def winner(self: "GameState", winner: Square) -> None:
        self._winner = winner

    def cycle_turn(self: "GameState") -> None:
        self.turn = next(self._turn_cycle)

    def make_move(self: "GameState", position: int) -> None:
        if position not in VALID_POSITIONS:
            raise IllegalMoveError
        if self.board[position] == Square.EMPTY:
            self.board[position] = self.turn
            self.cycle_turn()
            self.check_winner()
        else:
            raise IllegalMoveError

    def check_winner(self: "GameState") -> None:
        for a, b, c in WINNING_COMBINATIONS:
            if self.board[a] == self.board[b] == self.board[c] != Square.EMPTY:
                self.winner = self.board[a]
                raise GameOver
        if all(square != Square.EMPTY for square in self.board):
            raise GameOver

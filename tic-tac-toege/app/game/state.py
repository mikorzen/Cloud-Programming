from typing import Final

from models import Cell, Draw, GameOver, IllegalMoveError

# fmt: off
WINNING_COMBINATIONS: Final = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
    (0, 4, 8), (2, 4, 6),             # Diagonals
)  # fmt: on
VALID_POSITIONS: Final = [*range(9)]

class GameState:
    def __init__(self: "GameState") -> None:
        self._board = [Cell.EMPTY for _ in range(9)]
        self._turn = Cell.X
        self._winner = None

    @property
    def board(self: "GameState") -> list[Cell]:
        return self._board

    @property
    def turn(self: "GameState") -> Cell:
        return self._turn

    @property
    def winner(self: "GameState") -> Cell | None:
        return self._winner

    @turn.setter
    def turn(self: "GameState", value: Cell) -> None:
        self._turn = value

    @winner.setter
    def winner(self: "GameState", value: Cell) -> None:
        self._winner = value

    def make_move(self: "GameState", position: int) -> None:
        if position not in VALID_POSITIONS:
            raise IllegalMoveError
        if self.board[position] == Cell.EMPTY:
            self.board[position] = self.turn
            self.turn = Cell.X if self.turn == Cell.O else Cell.O
            self.check_winner()
        else:
            raise IllegalMoveError

    def check_winner(self: "GameState") -> None:
        for a, b, c in WINNING_COMBINATIONS:
            if self.board[a] == self.board[b] == self.board[c] != Cell.EMPTY:
                self.winner = self.board[a]
                raise GameOver(self.winner)
        if all(cell != Cell.EMPTY for cell in self.board):
            raise Draw

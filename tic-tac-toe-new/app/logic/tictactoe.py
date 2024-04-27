from typing import Final

# fmt: off
WINNING_COMBINATIONS: Final = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
    (0, 4, 8), (2, 4, 6),             # Diagonals
]  # fmt: on

class Draw(Exception):  # noqa: N818
    def __init__(self: "Draw") -> None:
        super().__init__("It's a draw")


class TicTacToe:
    def __init__(self: "TicTacToe") -> None:
        self._board = [" " for _ in range(9)]
        self._turn = "X"
        self._winner = None

    @property
    def board(self: "TicTacToe") -> list[str]:
        return self._board

    @property
    def turn(self: "TicTacToe") -> str:
        return self._turn

    @property
    def winner(self: "TicTacToe") -> str | None:
        return self._winner

    @turn.setter
    def turn(self: "TicTacToe", value: str) -> None:
        self._turn = value

    @winner.setter
    def winner(self: "TicTacToe", value: str) -> None:
        self._winner = value

    def make_move(self: "TicTacToe", position: int) -> bool:
        if self.board[position] == " " and not self.winner:
            self.board[position] = self.turn
            self.turn = "X" if self.turn == "O" else "O"
            return True if not self.check_winner() else False  # noqa: SIM210
        return False

    def check_winner(self: "TicTacToe") -> bool:
        for a, b, c in WINNING_COMBINATIONS:
            if self.board[a] == self.board[b] == self.board[c] != " ":
                self.winner = self.board[a]
                return True
        if all(square != " " for square in self.board):
            raise Draw
        return False

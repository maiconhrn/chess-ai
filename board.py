import chess

from config import *


class Board(chess.Board):
    def __init__(self):
        super().__init__()
        self.whiteScore = MAX_SCORE
        self.blackScore = MAX_SCORE
        self.endGame = False

    def push(self: chess.Board, move: chess.Move) -> None:
        if self.is_capture(move):
            if not self.is_en_passant(move):
                capturedPiece = self.piece_at(move.to_square)
                if capturedPiece.color == chess.WHITE:
                    self.whiteScore -= PIECE_VALUES[capturedPiece.piece_type]
                else:
                    self.blackScore -= PIECE_VALUES[capturedPiece.piece_type]
            else:
                attackPiece = self.piece_at(move.from_square)
                if attackPiece.color == chess.WHITE:
                    self.blackScore -= PIECE_VALUES[attackPiece.piece_type]
                else:
                    self.whiteScore -= PIECE_VALUES[attackPiece.piece_type]

        super().push(move)

    def pop(self: chess.Board) -> chess.Move:
        poppedMove = super().pop()

        if self.is_capture(poppedMove):
            if not self.is_en_passant(poppedMove):
                capturedPiece = self.piece_at(poppedMove.to_square)
                if capturedPiece.color == chess.WHITE:
                    self.whiteScore += PIECE_VALUES[capturedPiece.piece_type]
                else:
                    self.blackScore += PIECE_VALUES[capturedPiece.piece_type]
            else:
                attackPiece = self.piece_at(poppedMove.from_square)
                if attackPiece.color == chess.WHITE:
                    self.blackScore += PIECE_VALUES[attackPiece.piece_type]
                else:
                    self.whiteScore += PIECE_VALUES[attackPiece.piece_type]

        return poppedMove

    def gives_mate(self, move: chess.Move) -> bool:
        self.push(move)
        isMate = self.is_checkmate()
        self.pop()

        return isMate

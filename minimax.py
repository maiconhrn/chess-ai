#! /usr/bin/python3

from math import inf
from typing import Optional
import chess
import argparse
import chess.engine
from chess.svg import board


PIECE_VALUES = {
    "R": 50, "r": 50,
    "N": 30, "n": 30,
    "B": 30, "b": 30,
    "Q": 300, "q": 300,
    "K": 900, "k": 900,
    "P": 10, "p": 10,
}

MAX_SCORE = 1290


# nedded by error on use custom Board class with chess.Engine.play
boardAux = chess.Board()


class Board(chess.Board):
    def __init__(self):
        super().__init__()
        self.whiteScore = MAX_SCORE
        self.blackScore = MAX_SCORE

    def push(self: chess.BoardT, move: chess.Move) -> None:
        if self.is_capture(move):
            if not self.is_en_passant(move):
                capturedPiece = self.piece_at(move.to_square)
                if capturedPiece.color == chess.WHITE:
                    self.whiteScore -= PIECE_VALUES[str(capturedPiece)]
                else:
                    self.blackScore -= PIECE_VALUES[str(capturedPiece)]
            else:
                attackPiece = self.piece_at(move.from_square)
                if attackPiece.color == chess.WHITE:
                    self.blackScore -= PIECE_VALUES[str(attackPiece)]
                else:
                    self.whiteScore -= PIECE_VALUES[str(attackPiece)]

        super().push(move)

    def pop(self: chess.BoardT) -> chess.Move:
        poppedMove = super().pop()

        if self.is_capture(poppedMove):
            if not self.is_en_passant(poppedMove):
                capturedPiece = self.piece_at(poppedMove.to_square)
                if capturedPiece.color == chess.WHITE:
                    self.whiteScore += PIECE_VALUES[str(capturedPiece)]
                else:
                    self.blackScore += PIECE_VALUES[str(capturedPiece)]
            else:
                attackPiece = self.piece_at(poppedMove.from_square)
                if attackPiece.color == chess.WHITE:
                    self.blackScore += PIECE_VALUES[str(attackPiece)]
                else:
                    self.whiteScore += PIECE_VALUES[str(attackPiece)]

        return poppedMove


def evaluateHeuristic(board: Board, color: chess.Color):
    if color == chess.WHITE:
        return board.whiteScore - board.blackScore
    else:
        return board.blackScore - board.whiteScore


def minimax(board: Board, depth: int, maximizingPlayer: bool):
    if depth == 0 or board.is_game_over():
        return None, evaluateHeuristic(board, chess.WHITE)

    if maximizingPlayer:
        maxEval = -inf

        for move in board.legal_moves:
            board.push(move)
            currEval = minimax(board, depth - 1, False)[1]
            board.pop()
            if currEval > maxEval:
                maxEval = currEval
                bestMove = move

        return bestMove, maxEval
    else:
        minEval = inf
        for move in board.legal_moves:
            board.push(move)
            currEval = minimax(board, depth - 1, True)[1]
            board.pop()

            if currEval < minEval:
                minEval = currEval
                bestMove = move

        return bestMove, minEval


def printLegalMoves(board: Board):
    print("Legal moves: ", end='')
    for m in list(board.legal_moves):
        print(m, end=' ')
    print('')


def printBoard(board: Board):
    print("Current board: ")
    print(board)
    print("White score: " + str(board.whiteScore))
    print("Black score: " + str(board.blackScore))


def getArgs():
    parser = argparse.ArgumentParser(description="Play Chess.")
    parser.add_argument("-xe", "--xengine",
                        help="Engine path to play with minimax algorithm")
    return parser.parse_args()


def engineMove(board: Board, engine: chess.engine.SimpleEngine):
    move = engine.play(boardAux, chess.engine.Limit(time=0.1)).move
    board.push(move)
    boardAux.push(move)


def playerMove(board: Board):
    while True:
        moveInput = str(input("Enter move: "))
        try:
            move = chess.Move.from_uci(moveInput)
            if not board.is_legal(move):
                print("Illegal move: " + moveInput)
            else:
                board.push(move)
                boardAux.push(move)
                break
        except ValueError as e:
            print("Incorrect value: ", end='')
            print(e)


def minimaxMove(board: Board):
    print("Computer turn:")
    move = minimax(board, 4, True)[0]
    board.push(move)
    boardAux.push(move)


def main():
    args = getArgs()
    board = Board()

    n = 0
    printBoard(board)

    engine = args.xengine and chess.engine.SimpleEngine.popen_uci(args.xengine)

    if engine:
        engine.configure({"Skill Level": 1})

    while n < 100:
        if n % 2 == 0:
            printLegalMoves(board)
            engineMove(board, engine) if engine else playerMove(board)
        else:
            minimaxMove(board)

        n += 1

        printBoard(board)
        print("========================================", end="\n\n")


if __name__ == "__main__":
    main()

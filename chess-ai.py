#! /usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import random
import time
from math import inf

import chess
import chess.engine

from board import Board
from config import PIECE_VALUES
from tables import *

# nedded by error on use custom Board class with chess.Engine.play
boardAux = chess.Board()


def isEndGame(board: chess.Board):
    counter = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece:
            continue
        if piece.piece_type is not chess.PAWN and piece.piece_type is not chess.KING:
            counter += 1
            if counter > 4:
                return False

    return True


def piecesSqauredTableValuesHeuristic(piece: chess.Piece, square: chess.Square, maximizingColor: chess.Color, endGame: bool):
    row = square // 8
    column = square % 8

    if endGame and piece.piece_type == chess.KING:
        if piece.color == chess.WHITE:
            return KING_END_GAME_SQUARE_TABLE[row][column]
        else:
            return REVERSED_KING_END_GAME_SQUARE_TABLE[row][column]

    if piece.color == chess.WHITE:
        picesSquareTable = PIECE_SQUARE_TABLES.get(piece.piece_type)
    else:
        picesSquareTable = REVERSED_PIECE_SQUARE_TABLES.get(piece.piece_type)

    value = picesSquareTable[row][column]

    return value if piece.color == maximizingColor else -value


def defendingPieceMovesValuesHeuristic(board: Board, square: chess.Square, maximizingColor: chess.Color):
    if board.is_attacked_by(maximizingColor,  square):
        value = 30
    elif board.is_attacked_by(not maximizingColor,  square):
        value = -30
    else:
        value = 0

    return value


def piecesValuesHeuristic(board: Board, maximizingColor: chess.Color):
    if maximizingColor == chess.WHITE:
        return board.whiteScore - board.blackScore
    else:
        return board.blackScore - board.whiteScore


def evaluateHeuristic(board: Board, maximizingColor: chess.Color):
    h1 = h2 = h3 = 0

    h1 = piecesValuesHeuristic(board, maximizingColor)

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece:
            continue

        h2 += piecesSqauredTableValuesHeuristic(
            piece, square, maximizingColor, board.endGame)
        h3 += defendingPieceMovesValuesHeuristic(
            board, square, maximizingColor)

    return h1 + h2 + h3


def moveValue(board: chess.Board, move: chess.Move, maximizingColor: chess.Color, endgame: bool) -> float:
    if move.promotion is not None:
        return -float("inf") if board.turn != maximizingColor else float("inf")

    piece = board.piece_at(move.from_square)
    fromValue = piecesSqauredTableValuesHeuristic(
        piece, move.from_square, maximizingColor, endgame)
    toValue = piecesSqauredTableValuesHeuristic(
        piece, move.to_square, maximizingColor, endgame)
    positionChange = toValue - fromValue

    captureValue = 0.0
    if board.is_capture(move):
        captureValue = evaluateCapture(board, move)

    currentMoveValue = captureValue + positionChange
    if board.turn != maximizingColor:
        currentMoveValue = -currentMoveValue

    return currentMoveValue


def evaluateCapture(board: chess.Board, move: chess.Move) -> float:
    if board.is_en_passant(move):
        return PIECE_VALUES[chess.PAWN]
    toPiece = board.piece_at(move.to_square)
    fromPiece = board.piece_at(move.from_square)
    if toPiece is None or fromPiece is None:
        raise Exception(
            f"Pieces were expected at _both_ {move.to_square} and {move.from_square}"
        )
    return PIECE_VALUES[toPiece.piece_type] - PIECE_VALUES[fromPiece.piece_type]


def minimax(board: Board, depth: int, alpha: int, beta: int, maximizingPlayer: bool, maximizingColor: chess.Color):
    if depth == 0 or board.is_game_over():
        return None, evaluateHeuristic(board, maximizingColor)

    if maximizingPlayer:
        maxEval = -inf

        for move in board.legal_moves:
            board.push(move)
            currEval = minimax(board, depth - 1, alpha,
                               beta, False, maximizingColor)[1]
            board.pop()
            if currEval > maxEval:
                maxEval = currEval
                bestMove = move

            alpha = max(alpha, currEval)
            if beta <= alpha:
                break

        return bestMove, maxEval
    else:
        minEval = inf

        for move in board.legal_moves:
            board.push(move)
            currEval = minimax(board, depth - 1, alpha,
                               beta, True, maximizingColor)[1]
            board.pop()

            if currEval < minEval:
                minEval = currEval
                bestMove = move

            beta = min(beta, currEval)
            if beta <= alpha:
                break

        return bestMove, minEval


def randomStateMove(board: Board, depth: int, maximizingColor: chess.Color):
    moveValues = {}
    for _ in range(depth):
        move = random.choice(list(board.legal_moves))
        board.push(move)
        moveValues[evaluateHeuristic(board, maximizingColor)] = move
        board.pop()

    return moveValues[max(moveValues)]


def printLegalMoves(board: Board):
    print(
        f"Legal moves: {(', '.join(sorted([move.uci() for move in board.legal_moves])))}")


def printBoard(board: Board):
    print("Current board: ")
    print(board.unicode(invert_color=True, empty_square="."))
    print("White score: " + str(board.whiteScore))
    print("Black score: " + str(board.blackScore))


def getArgs():
    parser = argparse.ArgumentParser(description="Play Chess.")
    parser.add_argument("-d", "--depth", type=int,
                        help="Depth do search algorithm", required=True)
    parser.add_argument("-mmxe", "--mmxengine",
                        help="Engine path to play with minimax algorithm")
    parser.add_argument("-mmxi", "--mmxitself", type=bool,
                        help="Minimax vs minimax")
    parser.add_argument("-mmxr", "--mmxrandom", type=bool,
                        help="Minimax vs random move algorithm")
    parser.add_argument("-pxr", "--pxrandom", type=bool,
                        help="Player vs random move algorithm")
    parser.add_argument("-pxmm", "--pxminimax", type=bool,
                        help="Player vs minimax move algorithm")
    return parser.parse_args()


def engineMove(board: Board, engine: chess.engine.SimpleEngine):
    global boardAux
    move = engine.play(boardAux, chess.engine.Limit(time=0.1)).move
    board.push(move)
    boardAux.push(move)


def playerMove(board: Board):
    global boardAux
    while True:
        printLegalMoves(board)
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


def minimaxMove(board: Board, maximizingColor: chess.Color, depth: int):
    global boardAux
    move = minimax(board, depth, -inf, inf, True, maximizingColor)[0]
    board.push(move)
    boardAux.push(move)


def randomMove(board: Board, maximizingColor: chess.Color, depth: int):
    global boardAux
    move = randomStateMove(board, depth, maximizingColor)
    board.push(move)
    boardAux.push(move)


def who(player):
    return "White" if player == chess.WHITE else "Black"


def main():
    startTime = time.time()
    args = getArgs()
    board = Board()

    printBoard(board)

    engine = args.mmxengine and chess.engine.SimpleEngine.popen_uci(
        args.mmxengine)
    itself = args.mmxitself
    mmxrandom = args.mmxrandom
    playerXRandom = args.pxrandom
    playerXMinimax = args.pxminimax

    if engine:
        engine.configure({"Skill Level": 0})

    while not board.is_game_over():
        board.endGame = isEndGame(board)

        print(f"{who(board.turn)} turn:")
        if board.turn == chess.WHITE:
            if not playerXRandom and not playerXMinimax:
                if engine:
                    engineMove(board, engine)
                elif itself:
                    minimaxMove(board, chess.WHITE, args.depth)
                elif mmxrandom:
                    randomMove(board, chess.WHITE, args.depth)
            else:
                playerMove(board)
        else:
            if playerXMinimax or engine or itself or mmxrandom:
                minimaxMove(board, chess.BLACK, args.depth)
            else:
                randomMove(board, chess.BLACK, args.depth)

        printBoard(board)
        print("========================================", end="\n\n")

    print("Game over")
    if board.is_checkmate():
        msg = "Checkmate: " + who(not board.turn) + " wins!"
    elif board.is_stalemate():
        msg = "Draw: stalemate"
    elif board.is_fivefold_repetition():
        msg = "Draw: fivefold repetition"
    elif board.is_insufficient_material():
        msg = "Draw: insufficient material"
    elif board.can_claim_draw():
        msg = "Draw: claim"

    print(msg)
    print(f"Result: {board.result()}")
    print(f"Move qtd: {len(board.move_stack)}")
    print(f"Exec time: {(time.time() - startTime)}s")

    if engine:
        engine.quit()


if __name__ == "__main__":
    main()
    quit()

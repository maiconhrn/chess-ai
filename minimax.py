#! /usr/bin/python3

import argparse
from math import inf

import chess
import chess.engine

PIECES_VALUES = {
    chess.BISHOP: 330,
    chess.KING: 20000,
    chess.KNIGHT: 320,
    chess.PAWN: 100,
    chess.QUEEN: 900,
    chess.ROOK: 500,
}

MAX_SCORE = 23000

PIECE_SQUARED_TABLES = {
    chess.BISHOP: (
        (-20, -10, -10, -10, -10, -10, -10, -20),
        (-10,   0,   0,   0,   0,   0,   0, -10),
        (-10,   0,   5,  10,  10,   5,   0, -10),
        (-10,   5,   5,  10,  10,   5,   5, -10),
        (-10,   0,  10,  10,  10,  10,   0, -10),
        (-10,  10,  10,  10,  10,  10,  10, -10),
        (-10,   5,   0,   0,   0,   0,   5, -10),
        (-20, -10, -10, -10, -10, -10, -10, -20),
    ),
    chess.KING: (
        (-30, -40, -40, -50, -50, -40, -40, -30),
        (-30, -40, -40, -50, -50, -40, -40, -30),
        (-30, -40, -40, -50, -50, -40, -40, -30),
        (-30, -40, -40, -50, -50, -40, -40, -30),
        (-20, -30, -30, -40, -40, -30, -30, -20),
        (-10, -20, -20, -20, -20, -20, -20, -10),
        (20,  20,   0,   0,   0,   0,  20,  20),
        (20,  30,  10,   0,   0,  10,  30,  20),
    ),
    chess.KNIGHT: (
        (-50, -40, -30, -30, -30, -30, -40, -50),
        (-40, -20,   0,   0,   0,   0, -20, -40),
        (-30,   0,  10,  15,  15,  10,   0, -30),
        (-30,   5,  15,  20,  20,  15,   5, -30),
        (-30,   0,  15,  20,  20,  15,   0, -30),
        (-30,   5,  10,  15,  15,  10,   5, -30),
        (-40, -20,   0,   5,   5,   0, -20, -40),
        (-50, -40, -30, -30, -30, -30, -40, -50),
    ),
    chess.PAWN: (
        (0,   0,   0,   0,   0,   0,   0,   0),
        (50,  50,  50,  50,  50,  50,  50,  50),
        (10,  10,  20,  30,  30,  20,  10,  10),
        (5,   5,  10,  25,  25,  10,   5,   5),
        (0,   0,   0,  20,  20,   0,   0,   0),
        (5,  -5, -10,   0,   0, -10,  -5,   5),
        (5,  10,  10, -20, -20,  10,  10,   5),
        (0,   0,   0,   0,   0,   0,   0,   0),
    ),
    chess.QUEEN: (
        (-20, -10, -10,  -5,  -5, -10, -10, -20),
        (-10,   0,   0,   0,   0,   0,   0, -10),
        (-10,   0,   5,   5,   5,   5,   0, -10),
        (-5,   0,   5,   5,   5,   5,   0,  -5),
        (0,   0,   5,   5,   5,   5,   0,  -5),
        (-10,   5,   5,   5,   5,   5,   0, -10),
        (-10,   0,   5,   0,   0,   0,   0, -10),
        (-20, -10, -10,  -5,  -5, -10, -10, -20),
    ),
    chess.ROOK: (
        (0,   0,   0,   0,   0,   0,   0,   0),
        (5,  10,  10,  10,  10,  10,  10,   5),
        (-5,   0,   0,   0,   0,   0,   0,  -5),
        (-5,   0,   0,   0,   0,   0,   0,  -5),
        (-5,   0,   0,   0,   0,   0,   0,  -5),
        (-5,   0,   0,   0,   0,   0,   0,  -5),
        (-5,   0,   0,   0,   0,   0,   0,  -5),
        (0,   0,   0,   5,   5,   0,   0,   0),
    ),
}

PIECE_SQUARED_TABLES = {key: tuple(reversed(list(value)))
                        for key, value in PIECE_SQUARED_TABLES.items()}

REVERSED_PIECE_SQUARED_TABLES = {key: tuple([
                                            piece[::-1]
                                            for piece in value][::-1])
                                 for key, value in PIECE_SQUARED_TABLES.items()}

# nedded by error on use custom Board class with chess.Engine.play
boardAux = chess.Board()


class Board(chess.Board):
    def __init__(self):
        super().__init__()
        self.whiteScore = MAX_SCORE
        self.blackScore = MAX_SCORE

    def push(self: chess.Board, move: chess.Move) -> None:
        if self.is_capture(move):
            if not self.is_en_passant(move):
                capturedPiece = self.piece_at(move.to_square)
                if capturedPiece.color == chess.WHITE:
                    self.whiteScore -= PIECES_VALUES[capturedPiece.piece_type]
                else:
                    self.blackScore -= PIECES_VALUES[capturedPiece.piece_type]
            else:
                attackPiece = self.piece_at(move.from_square)
                if attackPiece.color == chess.WHITE:
                    self.blackScore -= PIECES_VALUES[attackPiece.piece_type]
                else:
                    self.whiteScore -= PIECES_VALUES[attackPiece.piece_type]

        super().push(move)

    def pop(self: chess.Board) -> chess.Move:
        poppedMove = super().pop()

        if self.is_capture(poppedMove):
            if not self.is_en_passant(poppedMove):
                capturedPiece = self.piece_at(poppedMove.to_square)
                if capturedPiece.color == chess.WHITE:
                    self.whiteScore += PIECES_VALUES[capturedPiece.piece_type]
                else:
                    self.blackScore += PIECES_VALUES[capturedPiece.piece_type]
            else:
                attackPiece = self.piece_at(poppedMove.from_square)
                if attackPiece.color == chess.WHITE:
                    self.blackScore += PIECES_VALUES[attackPiece.piece_type]
                else:
                    self.whiteScore += PIECES_VALUES[attackPiece.piece_type]

        return poppedMove

    def gives_mate(self, move: chess.Move) -> bool:
        self.push(move)
        isMate = self.is_checkmate()
        self.pop()

        return isMate


def moveGivesCheckValuesHeuristic(board: Board, move: chess.Move, maximizingColor: chess.Color):
    if board.gives_mate(move):
        return 1000 if board.color_at(move.from_square) == maximizingColor else -1000

    if board.gives_check(move):
        return 1 if board.color_at(move.from_square) == maximizingColor else -1

    return 0


def piecesMovesValuesHeuristic(board: Board, move: chess.Move, maximizingColor: chess.Color):
    squareValues = {"e4": 50, "e5": 50, "d4": 50, "d5": 50, "c6": 25, "d6": 25, "e6": 25, "f6": 25,
                    "c3": 25, "d3": 25, "e3": 25, "f3": 25, "c4": 25, "c5": 25, "f4": 25, "f5": 25}
    if move.to_square in squareValues:
        value = squareValues[move.to_square]   
        return value if board.turn == maximizingColor else -value
    else:
        return 0


def piecesSqauredTableValuesHeuristic(piece: chess.Piece, square: chess.Square, maximizingColor: chess.Color):
    row = square // 8
    column = square % 8

    if piece.color == chess.WHITE:
        picesSquaredTable = PIECE_SQUARED_TABLES.get(piece.piece_type)
    else:
        picesSquaredTable = REVERSED_PIECE_SQUARED_TABLES.get(piece.piece_type)

    value = picesSquaredTable[row][column]

    return value if piece.color == maximizingColor else -value


def defendingPieceMovesValuesHeuristic(board: Board, piece: chess.Piece, square: chess.Square, maximizingColor: chess.Color):
    if board.is_attacked_by(maximizingColor,  square):
        value = 10
    elif board.is_attacked_by(not maximizingColor,  square):
        value = -10
    else:
        value = 0

    return value


def piecesValuesHeuristic(board: Board, maximizingColor: chess.Color):
    if maximizingColor == chess.WHITE:
        return board.whiteScore - board.blackScore
    else:
        return board.blackScore - board.whiteScore


def evaluateHeuristic(board: Board, maximizingColor: chess.Color):
    h1 = h2 = h3 = h4 = h5 = 0

    h1 = piecesValuesHeuristic(board, maximizingColor)

    for move in board.legal_moves:
        h2 += piecesMovesValuesHeuristic(board, move, maximizingColor)
        h3 += moveGivesCheckValuesHeuristic(board, move, maximizingColor)

    for square in range(64):
        piece = board.piece_at(square)
        if not piece:
            continue

        h4 += piecesSqauredTableValuesHeuristic(piece, square, maximizingColor)
        h5 += defendingPieceMovesValuesHeuristic(
            board, piece, square, maximizingColor)

    return h1 * 40 + h2 * 10 + h3 * 20 + h4 * 20 + h5 * 10


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


def printLegalMoves(board: Board):
    print(
        f"Legal moves: {(', '.join(sorted([move.uci() for move in board.legal_moves])))}")


def printBoard(board: Board):
    print("Current board: ")
    print(board)
    print("White score: " + str(board.whiteScore))
    print("Black score: " + str(board.blackScore))


def getArgs():
    parser = argparse.ArgumentParser(description="Play Chess.")
    parser.add_argument("-xe", "--xengine",
                        help="Engine path to play with minimax algorithm")
    parser.add_argument("-xi", "--xitself", type=bool,
                        help="Minimax vs minimax")
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


def minimaxMove(board: Board, maximizingColor: chess.Color):
    global boardAux
    print("Computer turn:")
    move = minimax(board, 2, -inf, inf, True, maximizingColor)[0]
    board.push(move)
    boardAux.push(move)


def who(player):
    return "White" if player == chess.WHITE else "Black"


def main():
    args = getArgs()
    board = Board()

    printBoard(board)

    engine = args.xengine and chess.engine.SimpleEngine.popen_uci(args.xengine)
    itself = args.xitself

    if engine:
        engine.configure({"Skill Level": 1})

    while not board.is_game_over():
        if board.turn == chess.WHITE:
            if engine:
                engineMove(board, engine)
            elif itself:
                minimaxMove(board, chess.WHITE)
            else:
                playerMove(board)
        else:
            minimaxMove(board, chess.BLACK)

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
    print("Result: " + board.result())
    print(len(board.move_stack))

    raise SystemExit


if __name__ == "__main__":
    main()

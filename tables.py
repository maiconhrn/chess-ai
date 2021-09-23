import chess

PIECE_SQUARE_TABLES = {
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

KING_END_GAME_SQUARE_TABLE = (
    (-50, -40, -30, -20, -20, -30, -40, -50),
    (-30, -20, -10,   0,   0, -10, -20, -30),
    (-30, -10,  20,  30,  30,  20, -10, -30),
    (-30, -10,  30,  40,  40,  30, -10, -30),
    (-30, -10,  30,  40,  40,  30, -10, -30),
    (-30, -10,  20,  30,  30,  20, -10, -30),
    (-30, -30,   0,   0,   0,   0, -30, -30),
    (-50, -30, -30, -30, -30, -30, -30, -50),
)

PIECE_SQUARE_TABLES = {key: tuple(reversed(list(value)))
                       for key, value in PIECE_SQUARE_TABLES.items()}

KING_END_GAME_SQUARE_TABLE = tuple(
    reversed(list(KING_END_GAME_SQUARE_TABLE)))

REVERSED_PIECE_SQUARE_TABLES = {key: tuple([
    piece[::-1]
    for piece in value][::-1])
    for key, value in PIECE_SQUARE_TABLES.items()}

REVERSED_KING_END_GAME_SQUARE_TABLE = tuple([
    piece[::-1]
    for piece in KING_END_GAME_SQUARE_TABLE][::-1])

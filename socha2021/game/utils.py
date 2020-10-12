from enum import Enum
import random

class Move:
    def __init__(self, to, piece_type, piece_shape):
        self.piece_type = piece_type
        self.to = to
        self.piece_shape = piece_shape

    def __repr__(self):
        return f"Set {repr(self.piece_type)} to {self.to} (Shape {self.piece_shape})"

class Color(Enum):
    BLUE = 0
    YELLOW = 1
    RED = 2
    GREEN = 3

    def next(self):
        if self == Color.BLUE:
            return Color.YELLOW
        if self == Color.RED:
            return Color.GREEN
        if self == Color.YELLOW:
            return Color.RED
        return Color.BLUE

    def previous(self):
        if self == Color.YELLOW:
            return Color.BLUE
        if self == Color.GREEN:
            return Color.RED
        if self == Color.RED:
            return Color.YELLOW
        return Color.GREEN

class Piece(Enum):
    Monomino = 0
    Domino = 1
    ITromino = 2
    LTromino = 3
    ITetromino = 4
    LTetromino = 5
    TTetromino = 6
    OTetromino = 7
    ZTetromino = 8
    FPentomino = 9
    IPentomino = 10
    LPentomino = 11
    NPentomino = 12
    PPentomino = 13
    TPentomino = 14
    UPentomino = 15
    VPentomino = 16
    WPentomino = 17
    XPentomino = 18
    YPentomino = 19
    ZPentomino = 20

    def __repr__(self):
        return str(self)[6:]

    @staticmethod
    def random_pentomino():
        while True:
            idx = random.randint(9, 20)
            if idx != 18:
                return PIECE_TYPES[idx]

PIECE_TYPES = [
    Piece.Monomino,
    Piece.Domino,
    Piece.ITromino,
    Piece.LTromino,
    Piece.ITetromino,
    Piece.LTetromino,
    Piece.TTetromino,
    Piece.OTetromino,
    Piece.ZTetromino,
    Piece.FPentomino,
    Piece.IPentomino,
    Piece.LPentomino,
    Piece.NPentomino,
    Piece.PPentomino,
    Piece.TPentomino,
    Piece.UPentomino,
    Piece.VPentomino,
    Piece.WPentomino,
    Piece.XPentomino,
    Piece.YPentomino,
    Piece.ZPentomino
]

PIECE_TABLE = [
    [Piece.FPentomino, [[1, 23, 42, 43], [1, 21, 43, 44], [1, 2, 21, 43], [0, 1, 23, 43], [2, 21, 23, 43], [0, 21, 23, 43], [1, 21, 23, 44], [1, 21, 23, 42]], 51],
    [Piece.YPentomino, [[0, 22, 42, 63], [0, 21, 43, 63], [1, 22, 42, 64], [1, 21, 43, 64], [0, 1, 3, 23], [0, 2, 3, 22], [2, 21, 22, 24], [1, 21, 23, 24],], 83],
    [Piece.NPentomino, [[1, 42, 43, 63], [0, 42, 43, 64], [1, 21, 22, 63], [0, 21, 22, 64], [2, 3, 21, 23], [0, 2, 23, 24], [0, 1, 22, 24], [1, 3, 21, 22]], 63],
    [Piece.PPentomino, [[0, 1, 22, 42], [0, 1, 21, 43], [0, 1, 21, 23], [0, 2, 21, 22], [0, 2, 22, 23], [1, 2, 21, 23], [1, 21, 42, 43], [0, 22, 42, 43]], 75],
    [Piece.LPentomino, [[0, 3, 24], [0, 3, 21], [0, 21, 24], [3, 21, 24], [0, 1, 63], [0, 63, 64], [0, 1, 64], [1, 63, 64]], 23],
    [Piece.LTetromino, [[0, 1, 42], [0, 1, 43], [1, 43, 42], [0, 42, 43], [0, 21, 23], [0, 2, 21], [0, 2, 23], [2, 21, 23]], 15],
    [Piece.WPentomino, [[0, 21, 22, 43, 44], [2, 22, 23, 42, 43], [0, 1, 22, 23, 44], [1, 2, 21, 22, 42]], 59],
    [Piece.ZPentomino, [[0, 21, 23, 44], [2, 21, 23, 42], [1, 2, 42, 43], [0, 1, 43, 44]], 43],
    [Piece.ZTetromino, [[1, 2, 21, 22], [0, 1, 22, 23], [1, 21, 22, 42], [0, 21, 22, 43]], 39],
    [Piece.UPentomino, [[0, 2, 21, 23], [0, 2, 21, 23], [0, 1, 42, 43], [0, 1, 42, 43]], 47],
    [Piece.TTetromino, [[0, 2, 22], [1, 21, 23], [0, 22, 42], [1, 21, 43]], 35],
    [Piece.TPentomino, [[0, 2, 43], [1, 42, 44], [0, 23, 42], [2, 21, 44]], 31],
    [Piece.VPentomino, [[0, 2, 42], [2, 42, 44], [0, 2, 44], [0, 42, 44]], 71],
    [Piece.LTromino, [[0, 21, 22], [0, 1, 21], [0, 1, 22], [1, 21, 22]], 11],
    [Piece.XPentomino, [[0, 20, 22, 42]], 10],
    [Piece.OTetromino, [[0, 1, 21, 22]], 9],
    [Piece.IPentomino, [[0, 4], [0, 84]], 7],
    [Piece.ITetromino, [[0, 3], [0, 63]], 5],
    [Piece.ITromino, [[0, 2], [0, 42]], 3],
    [Piece.Domino, [[0, 1], [0, 21]], 1],
]

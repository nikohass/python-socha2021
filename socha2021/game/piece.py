from enum import Enum
import random

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

from enum import Enum
import random

class PieceType(Enum):
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

    def piece_size(self):
        if self.value == 0: return 1
        elif self.value < 2: return 2
        elif self.value < 4: return 3
        elif self.value < 9: return 4
        return 5

    def __repr__(self):
        return str(self)[10:]

    @staticmethod
    def random_pentomino():
        while True:
            piece_type = random.randint(9, 20)
            if piece_type != 18:
                return PieceType(piece_type)

    @staticmethod
    def from_shape(shape):
        if shape == 0: return PieceType.Monomino
        if shape < 3: return PieceType.Domino
        if shape < 5: return PieceType.ITromino
        if shape < 7: return PieceType.ITetromino
        if shape < 9: return PieceType.IPentomino
        if shape == 9: return PieceType.OTetromino
        if shape == 10: return PieceType.XPentomino
        if shape < 15: return PieceType.LTromino
        if shape < 23: return PieceType.LTetromino
        if shape < 31: return PieceType.LPentomino
        if shape < 35: return PieceType.TPentomino
        if shape < 39: return PieceType.TTetromino
        if shape < 43: return PieceType.ZTetromino
        if shape < 47: return PieceType.ZPentomino
        if shape < 51: return PieceType.UPentomino
        if shape < 59: return PieceType.FPentomino
        if shape < 63: return PieceType.WPentomino
        if shape < 71: return PieceType.NPentomino
        if shape < 75: return PieceType.VPentomino
        if shape < 83: return PieceType.PPentomino
        if shape < 92: return PieceType.YPentomino
        raise ValueError(f"Invalid shape: {shape}")

PIECE_TABLE = [
    [PieceType.FPentomino, [[1, 23, 42, 43], [1, 21, 43, 44], [1, 2, 21, 43], [0, 1, 23, 43], [2, 21, 23, 43], [0, 21, 23, 43], [1, 21, 23, 44], [1, 21, 23, 42]], 51],
    [PieceType.YPentomino, [[0, 22, 42, 63], [0, 21, 43, 63], [1, 22, 42, 64], [1, 21, 43, 64], [0, 1, 3, 23], [0, 2, 3, 22], [2, 21, 22, 24], [1, 21, 23, 24]], 83],
    [PieceType.NPentomino, [[1, 42, 43, 63], [0, 42, 43, 64], [1, 21, 22, 63], [0, 21, 22, 64], [2, 3, 21, 23], [0, 2, 23, 24], [0, 1, 22, 24], [1, 3, 21, 22]], 63],
    [PieceType.PPentomino, [[0, 1, 22, 42], [0, 1, 21, 43], [0, 1, 21, 23], [0, 2, 21, 22], [0, 2, 22, 23], [1, 2, 21, 23], [1, 21, 42, 43], [0, 22, 42, 43]], 75],
    [PieceType.LPentomino, [[0, 3, 24], [0, 3, 21], [0, 21, 24], [3, 21, 24], [0, 1, 63], [0, 63, 64], [0, 1, 64], [1, 63, 64]], 23],
    [PieceType.LTetromino, [[0, 1, 42], [0, 1, 43], [1, 43, 42], [0, 42, 43], [0, 21, 23], [0, 2, 21], [0, 2, 23], [2, 21, 23]], 15],
    [PieceType.WPentomino, [[0, 21, 22, 43, 44], [2, 22, 23, 42, 43], [0, 1, 22, 23, 44], [1, 2, 21, 22, 42]], 59],
    [PieceType.ZPentomino, [[0, 21, 23, 44], [2, 21, 23, 42], [1, 2, 42, 43], [0, 1, 43, 44]], 43],
    [PieceType.ZTetromino, [[1, 2, 21, 22], [0, 1, 22, 23], [1, 21, 22, 42], [0, 21, 22, 43]], 39],
    [PieceType.UPentomino, [[0, 2, 21, 23], [0, 2, 21, 23], [0, 1, 42, 43], [0, 1, 42, 43]], 47],
    [PieceType.TTetromino, [[0, 2, 22], [1, 21, 23], [0, 22, 42], [1, 21, 43]], 35],
    [PieceType.TPentomino, [[0, 2, 43], [1, 42, 44], [0, 23, 42], [2, 21, 44]], 31],
    [PieceType.VPentomino, [[0, 2, 42], [2, 42, 44], [0, 2, 44], [0, 42, 44]], 71],
    [PieceType.LTromino, [[0, 21, 22], [0, 1, 21], [0, 1, 22], [1, 21, 22]], 11],
    [PieceType.XPentomino, [[1, 21, 23, 43]], 10],
    [PieceType.OTetromino, [[0, 1, 21, 22]], 9],
    [PieceType.IPentomino, [[0, 4], [0, 84]], 7],
    [PieceType.ITetromino, [[0, 3], [0, 63]], 5],
    [PieceType.ITromino, [[0, 2], [0, 42]], 3],
    [PieceType.Domino, [[0, 1], [0, 21]], 1],
]

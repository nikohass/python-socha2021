from blokus.piece_type import PieceType
from blokus.bitboard import Bitboard

class Action:
    def __init__(self, to, shape):
        self.to = to
        self.shape = shape
        self.piece_type = PieceType.from_shape(shape)

    def serialize(action):
        if action == None:
            return "Skip"
        return f"{action.to} {action.shape}"

    @staticmethod
    def deserialize(value):
        if value == 0xFFFF:
            return None
        shape = value & 0b1111111
        to = value >> 7
        return Action(to, shape)

    @staticmethod
    def from_bitboard(board):
        original_board = board.clone()
        left = top = 21
        while board.fields != 0:
            field_index = board.trailing_zeros()
            board.flip_bit(field_index)
            x = field_index % 21
            y = (field_index - x) // 21
            if y < top:
                top = y
            if x < left:
                left = x
        to = left + top * 21
        for shape in range(91):
            if Bitboard.with_piece(to, shape) == original_board:
                return Action(to, shape)
        print("Can't determine action from Bitboard")
        print(original_board)

    def __eq__(self, other):
        return other != None and self.shape == other.shape and self.to == other.to

    def __repr__(self):
        return f"Set {repr(self.piece_type)} to {self.to} (X={self.to % 21} Y={(self.to - (self.to % 21)) // 21} Shape={self.shape})"

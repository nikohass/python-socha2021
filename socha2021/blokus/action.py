from blokus.piece_type import PieceType
from blokus.bitboard import Bitboard

class Action:
    def __init__(self, destination, shape):
        self.destination = destination
        self.shape = shape
        self.piece_type = PieceType.from_shape(shape)

    @staticmethod
    def serialize(action):
        if action == None:
            return 0xFFFF
        return f"{action.destination << 7 | action.shape}"

    @staticmethod
    def deserialize(value):
        if value == 0xFFFF:
            return None
        shape = value & 0b1111111
        destination = value >> 7
        return Action(destination, shape)

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
        destination = left + top * 21
        for shape in range(91):
            if Bitboard.with_piece(destination, shape) == original_board:
                return Action(destination, shape)
        print("Can't determine action from Bitboard")
        print(original_board)

    def __eq__(self, other):
        return other != None and self.shape == other.shape and self.destination == other.destination

    def __repr__(self):
        return f"Set {repr(self.piece_type)} to {self.destination} (X={self.destination % 21} Y={(self.destination - (self.destination % 21)) // 21} Shape={self.shape})"

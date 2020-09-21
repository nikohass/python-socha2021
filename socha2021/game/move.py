from piece import Piece

class Move:
    def __init__(self, to: int, piece_type: Piece, piece_shape: int):
        self.piece_type = piece_type
        self.to = to
        self.piece_shape = piece_shape

    def __repr__(self):
        return f"Set {repr(self.piece_type)} to {self.to} (Shape {self.piece_shape})"

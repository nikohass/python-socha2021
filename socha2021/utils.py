from blokus import *
import numpy as np

INPUT_DIMS = 1692
OUTPUT_DIMS = 400

class Rotation:
    def __init__(self, mirror: bool, top_left_corner: int):
        self.mirror = mirror
        self.top_left_corner = top_left_corner
        assert self.top_left_corner < 4

    def rotate_bitboard(self, bitboard: Bitboard) -> Bitboard:
        if self.top_left_corner == 1:
            bitboard = bitboard.mirror()
        elif self.top_left_corner == 2:
            bitboard = bitboard.flip()
        elif self.top_left_corner == 3:
            bitboard = bitboard.rotate_left().rotate_left()
        return bitboard.mirror() if self.mirror else bitboard

    def rotate_state(self, state: GameState):
        for i, b in enumerate(state.board):
            state.board[i] = self.rotate_bitboard(b)
        return state

    def rotate_action(self, action: Action): # very slow
        piece_type = action.piece_type
        action = Action.from_bitboard(self.rotate_bitboard(Bitboard.with_piece(action.to, action.shape_index)))
        action.piece_type = piece_type
        return action

    @staticmethod
    def from_state(state: GameState):
        current_color = state.current_color.value
        top_left_corner = 3
        for i, corner in enumerate([0, 19, 399]):
            if state.board[current_color].check_bit(corner):
                top_left_corner = i
                break
        mirror = False
        for a, b in [(1, 21), (2, 42), (23, 43), (24, 64)]:
            c = state.board[current_color].check_bit(a)
            d = state.board[current_color].check_bit(b)
            if c and not d:
                mirror = True
                break
            if not c and d:
                break
        return Rotation(mirror, top_left_corner)

def state_to_array(state: GameState) -> np.array:
    array = np.zeros(shape=(INPUT_DIMS,))
    color_order = [(state.current_color.value + i) % 4 for i in range(4)]
    index = 0
    # board
    for color in color_order:
        for x in range(20):
            for y in range(20):
                if state.board[color].check_bit(x + y * 21):
                    array[index] = 1
                index += 1
    # remaining pieces
    for color in color_order:
        for i in range(21):
            if state.pieces_left[i][color]:
                array[index] = 1
            index += 1
    # ply
    for i in range(8):
        array[index + i] = 1 if state.ply & (1 << i) != 0 else 0
    return array

def array_to_state(array: np.array) -> GameState:
    assert array.shape == (INPUT_DIMS,)
    state = GameState()
    # ply
    for i in range(INPUT_DIMS - 8, INPUT_DIMS):
        state.ply |= int(1 if array[i] > 0.5 else 0) << (i - INPUT_DIMS + 8)
    state.current_color = Color.from_ply(state.ply)
    color_order = reversed([(state.current_color.value - 1 - i) % 4 for i in range(4)])
    index = 0
    # board
    for color in color_order:
        for x in range(20):
            for y in range(20):
                if array[index] > 0.5:
                    state.board[color].flip_bit(x + y * 21)
                index += 1
    # remaining pieces
    for color in color_order:
        for i in range(21):
            state.pieces_left[i] = array[index] > 0.5
            index += 1
    return state

def bitboard_to_array(board: Bitboard) -> np.array:
    array = np.zeros(shape=(OUTPUT_DIMS,))
    for x in range(20):
        for y in range(20):
            if board.check_bit(x + y * 21):
                array[x + y * 20] = 1
    return array

def array_to_bitboard(array: np.array) -> Bitboard:
    assert array.shape == (OUTPUT_DIMS,)
    board = Bitboard()
    for x in range(20):
        for y in range(20):
            if array[x + y * 20] > 0.5:
                board.flip_bit(x + y * 21)
    return board

def load_datasets(paths):
    X = []
    Y = []
    length = 0
    for path in paths if type(paths) == list else [paths]:
        print(f"loading \"{path}\"...")
        with open(path, "r") as file:
            line_index = 0
            for line in file:
                try:
                    line = line.strip()
                    state = GameState.from_fen(line)
                    action = Action.deserialize(line.split()[18:])
                    rotation = Rotation.from_state(state)
                    rotation.rotate_state(state)
                    X.append(state_to_array(state))
                    Y.append(bitboard_to_array(rotation.rotate_bitboard(Bitboard.with_piece(action.to, action.shape_index))))
                    length += 1
                except Exception as e:
                    print(f"Exception (Line {line_index} in {path}):", e)
                if length % 10_000 == 0:
                    print(length)
                if length > 500_000: break
                line_index += 1
    return np.array(X), np.array(Y)

if __name__ == "__main__":
    # tests
    import copy

    for _ in range(10):
        state = GameState.random(10)
        rotation = Rotation.from_state(state)
        for i in range(4):
            assert state.board[i] == rotation.rotate_bitboard(rotation.rotate_bitboard(state.board[i]))
            assert state.board[i] == array_to_bitboard(bitboard_to_array(state.board[i]))
        assert state.board == rotation.rotate_state(rotation.rotate_state(copy.deepcopy(state))).board
        assert state.board == array_to_state(state_to_array(state)).board

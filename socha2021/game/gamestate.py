from bitboard import *
from color import Color
from piece import PIECE_TYPES, Piece
from move import Move

BLUE = Color.BLUE.value
YELLOW = Color.YELLOW.value
RED = Color.RED.value
GREEN = Color.GREEN.value

PIECE_TABLE = [
    [Piece.LPentomino, [[0, 3, 24], [0, 3, 21], [0, 21, 24], [3, 21, 24], [0, 1, 63], [0, 63, 64], [0, 1, 64], [1, 63, 64]], 23],
    [Piece.TPentomino, [[0, 2, 43], [1, 42, 44], [0, 23, 42], [2, 21, 44]], 31],
    [Piece.ZPentomino, [[0, 21, 23, 44], [2, 21, 23, 42], [1, 2, 42, 43], [0, 1, 43, 44]], 43],
    [Piece.UPentomino, [[0, 2, 21, 23], [0, 2, 21, 23], [0, 1, 42, 43], [0, 1, 42, 43]], 47],
    [Piece.FPentomino, [[1, 23, 42, 43], [1, 21, 43, 44], [1, 2, 21, 43], [0, 1, 23, 43], [2, 21, 23, 43], [0, 21, 23, 43], [1, 21, 23, 44], [1, 21, 23, 42]], 51],
    [Piece.WPentomino, [[0, 21, 22, 43, 44], [2, 22, 23, 42, 43], [0, 1, 22, 23, 44], [1, 2, 21, 22, 42]], 59],
    [Piece.NPentomino, [[1, 42, 43, 63], [0, 42, 43, 64], [1, 21, 22, 63], [0, 21, 22, 64], [2, 3, 21, 23], [0, 2, 23, 24], [0, 1, 22, 24], [1, 3, 21, 22]], 63],
    [Piece.VPentomino, [[0, 2, 42], [2, 42, 44], [0, 2, 44], [0, 42, 44]], 71],
    [Piece.PPentomino, [[0, 1, 22, 42], [0, 1, 21, 43], [0, 1, 21, 23], [0, 2, 21, 22], [0, 2, 22, 23], [1, 2, 21, 23], [1, 21, 42, 43], [0, 22, 42, 43]], 75],
    [Piece.YPentomino, [[0, 22, 42, 63], [0, 21, 43, 63], [1, 22, 42, 64], [1, 21, 43, 64], [0, 1, 3, 23], [0, 2, 3, 22], [2, 21, 22, 24], [1, 21, 23, 24],], 83],
    [Piece.TTetromino, [[0, 2, 22], [1, 21, 23], [0, 22, 42], [1, 21, 43]], 35],
    [Piece.OTetromino, [[0, 1, 21, 22]], 9],
    [Piece.ZTetromino, [[1, 2, 21, 22], [0, 1, 22, 23], [1, 21, 22, 42], [0, 21, 22, 43]], 39],
    [Piece.LTetromino, [[0, 1, 42], [0, 1, 43], [1, 43, 42], [0, 42, 43], [0, 21, 23], [0, 2, 21], [0, 2, 23], [2, 21, 23]], 15],
    [Piece.LTromino, [[0, 21, 22], [0, 1, 21], [0, 1, 22], [1, 21, 22]], 11],
]

class GameState:
    def __init__(self):
        self.ply = 0
        self.board = [Bitboard() for _ in range(4)]
        self.pieces_left = [[True for _ in range(4)] for _ in range(21)]
        self.monomino_placed_last = [False for _ in range(4)]
        self.start_piece_type = Piece.random_pentomino()
        self.skipped = 0
        self.current_player = Color.BLUE

    def do_move(self, move):
        if move == None:
            self.current_player = Color.next(self.current_player)
            self.ply += 1
            self.skipped |= 1 << self.current_player.value
            return

        current_player = self.current_player.value
        piece = Bitboard.with_piece(move.to, move.piece_shape)
        self.skipped &= ~1 << self.current_player.value
        self.pieces_left[move.piece_type.value][current_player] = False
        self.board[current_player] ^= piece
        self.monomino_placed_last[current_player] = move.piece_type == Piece.Monomino
        self.current_player = Color.next(self.current_player)
        self.ply += 1

    def get_possible_moves(self):
        move_list = []
        own_fields = self.board[self.current_player.value]
        other_fields = (self.board[0] | self.board[1] | self.board[2] | self.board[3]) & ~own_fields
        legal_fields = ~(own_fields | other_fields | own_fields.neighbours()) & VALID_FIELDS
        placement_fields = own_fields.diagonal_neighbours() & legal_fields if self.ply > 3 else START_FIELDS & ~other_fields
        with_two_in_a_row = placement_fields & (legal_fields << 1 | legal_fields >> 1 | legal_fields << 21 | legal_fields >> 21)
        with_three_in_a_row = with_two_in_a_row & (legal_fields << 2 | legal_fields >> 2 | legal_fields << 42 | legal_fields >> 42)
        assert own_fields & VALID_FIELDS == own_fields
        assert other_fields & VALID_FIELDS == other_fields

        for d in DIRECTIONS:
            two_in_a_row = legal_fields & placement_fields.neighbours_in_direction(d)
            three_in_a_row = legal_fields & two_in_a_row.neighbours_in_direction(d)
            four_in_a_row = legal_fields & three_in_a_row.neighbours_in_direction(d)
            five_in_a_row = legal_fields & four_in_a_row.neighbours_in_direction(d)

            if self.pieces_left[Piece.Domino.value][self.current_player.value]:
                while two_in_a_row.fields != 0:
                    to = two_in_a_row.trailing_zeros()
                    two_in_a_row.flip_bit(to)
                    if d == "RIGHT":
                        move_list.append(Move(to, Piece.Domino, 1))
                    elif d == "LEFT":
                        move_list.append(Move(to - 1, Piece.Domino, 1))
                    elif d == "UP":
                        move_list.append(Move(to - 21, Piece.Domino, 2))
                    else:
                        move_list.append(Move(to, Piece.Domino, 2))

            if self.pieces_left[Piece.ITromino.value][self.current_player.value]:
                while three_in_a_row.fields != 0:
                    to = three_in_a_row.trailing_zeros()
                    three_in_a_row.flip_bit(to)
                    if d == "RIGHT":
                        move_list.append(Move(to, Piece.ITromino, 3))
                    elif d == "LEFT":
                        move_list.append(Move(to - 2, Piece.ITromino, 3))
                    elif d == "UP":
                        move_list.append(Move(to - 42, Piece.ITromino, 4))
                    else:
                        move_list.append(Move(to, Piece.ITromino, 4))

            if self.pieces_left[Piece.ITetromino.value][self.current_player.value]:
                while four_in_a_row.fields != 0:
                    to = four_in_a_row.trailing_zeros()
                    four_in_a_row.flip_bit(to)
                    if d == "RIGHT":
                        move_list.append(Move(to, Piece.ITetromino, 5))
                    elif d == "LEFT":
                        move_list.append(Move(to - 3, Piece.ITetromino, 5))
                    elif d == "UP":
                        move_list.append(Move(to - 63, Piece.ITetromino, 6))
                    else:
                        move_list.append(Move(to, Piece.ITetromino, 6))

            if self.pieces_left[Piece.IPentomino.value][self.current_player.value]:
                while five_in_a_row.fields != 0:
                    to = five_in_a_row.trailing_zeros()
                    five_in_a_row.flip_bit(to)
                    if d == "RIGHT":
                        move_list.append(Move(to, Piece.IPentomino, 7))
                    elif d == "LEFT":
                        move_list.append(Move(to - 4, Piece.IPentomino, 7))
                    elif d == "UP":
                        move_list.append(Move(to - 84, Piece.IPentomino, 8))
                    else:
                        move_list.append(Move(to, Piece.IPentomino, 8))

        for p in PIECE_TABLE:
            if self.pieces_left[p[0].value][self.current_player.value]:
                candidates = placement_fields.copy()
                while candidates.fields != 0:
                    to = candidates.trailing_zeros()
                    candidates.flip_bit(to)
                    shape_index = p[2]
                    for offsets in p[1]:
                        for offset in offsets:
                            if to >= offset:
                                piece = Bitboard.with_piece(to - offset, shape_index)
                                if piece & legal_fields == piece:
                                    move_list.append(Move(to - offset, p[0], shape_index))
                        shape_index += 1

        if self.pieces_left[Piece.XPentomino.value][self.current_player.value]:
            candidates = with_three_in_a_row.copy()
            while candidates.fields != 0:
                to = candidates.trailing_zeros()
                candidates.flip_bit(to)
                for offset in [0, 20, 22, 42]:
                    if to >= offset:
                        destination = to - offset
                        piece = Bitboard.with_piece(destination, 10)
                        if piece & legal_fields == piece:
                            move_list.append(Move(destination, Piece.XPentomino, 10))

        if self.pieces_left[Piece.Monomino.value][self.current_player.value]:
            while placement_fields.fields != 0:
                to = placement_fields.trailing_zeros()
                placement_fields.flip_bit(to)
                move_list.append(Move(to, Piece.Monomino, 0))

        if self.ply < 4:
            return [move for move in move_list if move.piece_type == self.start_piece_type]
        return move_list
            
    def is_game_over(self):
        return self.skipped == 15 or self.ply / 4 == 26

    def game_result(self):
        scores = [self.board[color].count_ones() for color in range(4)]

        for color in range(4):
            if scores[color] == 89:
                if self.monomino_placed_last[color]:
                    scores[color] += 20
                else:
                    scores[color] += 15

        return scores[0] + scores[1] - scores[2] - scores[3]

    def int_to_piece_info(self, info):
        self.skipped = info >> 120
        for player_index in range(4):
            self.monomino_placed_last[player_index] = (1 << player_index) & info != 0
            for i in range(21):
                self.pieces_left[i][player_index] = info & 1 << (i + 21 * player_index + 4) != 0
        start_piece_index = info >> 110 & 31
        self.start_piece_type = PIECE_TYPES[start_piece_index]

    @staticmethod
    def from_fen(fen):
        state = GameState()
        entries = [int(entry) for entry in fen.split(" ")]
        assert len(entries) == 18
        state.ply = entries[0]
        for b in range(4):
            state.board[b].fields = entries[b * 4 + 1] << 384 | entries[b * 4 + 2] << 256 | entries[b * 4 + 3] << 128 | entries[b * 4 + 4]
        state.current_player = Color.BLUE if state.ply % 4 == 0 else Color.YELLOW if state.ply % 4 == 1 else \
                               Color.RED if state.ply % 4 == 2 else Color.GREEN
        state.int_to_piece_info(entries[-1])
        return state

    def __repr__(self):
        string = "╔" + "═" * 40 + "╗\n" + f"║ {self.current_player} Turn: {self.ply} Round: {int(self.ply/4)}"
        string += " " * (84 - len(string)) + "║\n" + "╠" + "═" * 40 + "╣"
        for i in range(20):
            string += "\n║"
            for j in range(20):
                y = 19 - i
                x = j
                field_index = x + y * 21
                bit = 1 << field_index
                if self.board[0].fields & bit != 0:
                    string += "🟦"
                elif self.board[1].fields & bit != 0:
                    string += "🟨"
                elif self.board[2].fields & bit != 0:
                    string += "🟥"
                elif self.board[3].fields & bit != 0:
                    string += "🟩"
                else:
                    string += "▪ "
            string += "║"
        string += "\n╚" + "═" * 40 + "╝"
        return string

from random import choice
state = GameState()
while not state.is_game_over():
    move_list = state.get_possible_moves()
    state.do_move(None if len(move_list) == 0 else choice(move_list))
    print(state)
print(state.game_result())

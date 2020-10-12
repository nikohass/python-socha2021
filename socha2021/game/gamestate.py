from bitboard import *
from utils import *

class GameState:
    def __init__(self):
        self.ply = self.skipped = 0
        self.board = [Bitboard() for _ in range(4)]
        self.start_piece_type = Piece.random_pentomino()
        self.pieces_left = [[True for _ in range(4)] for _ in range(21)]
        self.monomino_placed_last = [False for _ in range(4)]
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
        assert own_fields & VALID_FIELDS == own_fields
        assert other_fields & VALID_FIELDS == other_fields

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

        if self.pieces_left[Piece.Monomino.value][self.current_player.value]:
            while placement_fields.fields != 0:
                to = placement_fields.trailing_zeros()
                placement_fields.flip_bit(to)
                move_list.append(Move(to, Piece.Monomino, 0))

        if self.ply < 4:
            move_list = [move for move in move_list if move.piece_type == self.start_piece_type]
        return move_list if len(move_list) != 0 else [None]

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

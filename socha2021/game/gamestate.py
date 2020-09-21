from bitboard import *
from color import Color
from piece import PIECE_TYPES, Piece
from move import Move

BLUE = Color.BLUE.value
YELLOW = Color.YELLOW.value
RED = Color.RED.value
GREEN = Color.GREEN.value

class GameState:
    def __init__(self):
        self.ply = 0
        self.board = [Bitboard() for _ in range(4)]
        self.pieces_left = [[True for _ in range(4)] for _ in range(21)]
        self.monomino_placed_last = [False for _ in range(4)]
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

    def get_possible_moves(self, move_list):
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
gs = (GameState.from_fen("20 32768 15950743555472498867215306974539284496 1298074833604611993819774835491712 83076749736557242056487941267521536 17179881472 1993842300686507093905443867859091584 41538513517600800102841821851287552 0 0 0 62914569 170143901305290402726619173899970019335 0 0 155648 38547617899104724787858147799116677120 16874964943690196498745885797924848"))
for _ in range(30):
    move_list = []
    gs.get_possible_moves(move_list)
    print(gs)
    print(move_list)
    gs.do_move(None if len(move_list) == 0 else choice(move_list))
    print(gs)
    print(gs.skipped)
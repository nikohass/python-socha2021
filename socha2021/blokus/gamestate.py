import random
from blokus.bitboard import *
from blokus.action import Action
from blokus.color import Color
from blokus.piece_type import *

class GameState:
    def __init__(self, fen=None):
        self.ply = 0
        self.skipped = 0
        self.board = [Bitboard() for _ in range(5)]
        self.start_piece_type = PieceType.random_pentomino()
        self.pieces_left = [[True] * 4 for _ in range(21)]
        self.monomino_placed_last = [False] * 4
        self.current_color = Color.BLUE
        if fen != None:
            self.load_fen(fen)

    def do_action(self, action):
        if action == None:
            self.skipped = ((self.skipped & 0b1111) | self.skipped << 4) | (1 << self.current_color.value)
        else:
            self.pieces_left[action.piece_type.value][self.current_color.value] = False
            self.board[self.current_color.value] ^= Bitboard.with_piece(action.destination, action.shape)
            self.monomino_placed_last[self.current_color.value] = action.piece_type == PieceType.Monomino
        self.current_color = self.current_color.next()
        self.ply += 1

    def undo_action(self, action):
        self.ply -= 1
        self.current_color = self.current_color.previous()
        if action == None:
            self.skipped >>= 4
        else:
            piece = Bitboard.with_piece(action.destination, action.shape)
            self.pieces_left[action.piece_type.value][self.current_color.value] = True
            self.board[self.current_color.value] ^= piece

    def get_occupied_fields(self):
        return self.board[0] | self.board[1] | self.board[2] | self.board[3]

    def get_possible_actions(self):
        possible_actions = []
        own_fields = self.board[self.current_color.value]
        other_fields = self.get_occupied_fields() & ~own_fields
        legal_fields = ~(own_fields | other_fields | own_fields.neighbours()) & VALID_FIELDS
        if self.ply > 3:
            placement_fields = own_fields.diagonal_neighbours() & legal_fields
        else:
            placement_fields = START_FIELDS & ~other_fields

        for piece_type in PIECE_TABLE:
            if not self.pieces_left[piece_type[0].value][self.current_color.value]:
                continue
            candidates = placement_fields.clone()
            for candidate_field in candidates:
                shape = piece_type[2]
                for offsets in piece_type[1]:
                    for offset in offsets:
                        if candidate_field >= offset:
                            destination = candidate_field - offset
                            piece = Bitboard.with_piece(destination, shape)
                            if piece & legal_fields == piece:
                                possible_actions.append(Action(destination, shape))
                    shape += 1

        if self.pieces_left[PieceType.Monomino.value][self.current_color.value]:
            for destination in placement_fields:
                possible_actions.append(Action(destination, 0))

        if self.ply < 4:
            return [action for action in possible_actions if action.piece_type == self.start_piece_type]
        if len(possible_actions) != 0:
            return possible_actions
        return [None]

    def is_game_over(self):
        return self.skipped & 0b1111 == 0b1111 or self.ply > 100

    def game_result(self):
        scores = [self.board[color].count_ones() for color in range(4)]
        for color in range(4):
            if scores[color] == 89:
                scores[color] += 15
                if self.monomino_placed_last[color]:
                    scores[color] += 5
        return scores[0] + scores[2] - scores[1] - scores[3]

    def load_fen(self, fen):
        entries = [int(entry) for entry in fen.split(" ")[:18]]
        assert len(entries) == 18
        data = entries[0]
        for i in range(4):
            self.monomino_placed_last[i] = data & 1 << i != 0
        self.start_piece_type = PieceType(data >> 4 & 0b11111)
        self.ply = data >> 9 & 0b11111111
        self.current_color = Color.from_ply(self.ply)
        self.skipped = data >> 17
        pieces = entries[1]
        for color in range(4):
            for piece_type in range(21):
                if pieces & 1 << (piece_type + color * 21) != 0:
                    self.pieces_left[piece_type][color] = False
            self.board[color].fields = entries[color * 4 + 2] << 384
            self.board[color].fields |= entries[color * 4 + 3] << 256
            self.board[color].fields |= entries[color * 4 + 4] << 128
            self.board[color].fields |= entries[color * 4 + 5]
        return entries

    def to_fen(self):
        data = self.start_piece_type.value << 4
        data |= self.ply << 9
        data |= self.skipped << 17
        pieces = 0
        for color in range(4):
            if self.monomino_placed_last[color]:
                data |= 1 << color
            for piece_type in range(21):
                if not self.pieces_left[piece_type][color]:
                    pieces |= 1 << (piece_type + color * 21)
        return f"{data} {pieces} {self.board[0].to_fen()} {self.board[1].to_fen()} {self.board[2].to_fen()} {self.board[3].to_fen()}"

    @staticmethod
    def random(n=8):
        state = GameState()
        for _ in range(n):
            state.do_action(random.choice(state.get_possible_actions()))
        return state

    def __repr__(self):
        string = "╔" + "═" * 40 + "╗\n" + f"║ {self.current_color} Turn: {self.ply} Score: {self.game_result()}"
        string += " " * (83 - len(string)) + "║\n" + "╠" + "═" * 40 + "╣"
        for y in range(20):
            string += "\n║"
            for x in range(20):
                field_index = convert(x, y)
                for color in range(5):
                    if self.board[color].check_bit(field_index) != 0:
                        string += ["🟦", "🟨", "🟥", "🟩", "🟧"][color]
                        break
                else:
                    string += "▪ "
            string += "║"
        string += "\n╚" + "═" * 40 + "╝"
        return string

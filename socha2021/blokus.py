import random
from enum import Enum

class Bitboard:
    def __init__(self, fields=0):
        self.fields = fields

    def flip_bit(self, bit_idx):
        self.fields ^= 1 << bit_idx

    def check_bit(self, bit_idx):
        return self.fields & (1 << bit_idx) != 0

    def print_parts(self):
        print("one  ", self.fields >> 384 & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
        print("two  ", self.fields >> 256 & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
        print("three", self.fields >> 128 & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
        print("four ", self.fields & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)

    def to_parts(self):
        return (self.fields >> 384 & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            self.fields >> 256 & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            self.fields >> 128 & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            self.fields & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)

    def count_ones(self):
        ones = 0
        bit = 1
        board_copy = self.fields
        while board_copy != 0:
            if bit & board_copy != 0:
                ones += 1
                board_copy ^= bit
            bit <<= 1
        return ones

    def trailing_zeros(self):
        bit = 1
        for i in range(512):
            if bit & self.fields == bit:
                return i
            bit <<= 1
        return 512

    def flip(self):
        board = Bitboard()
        for row in range(20):
            board |= (self >> (21 * row) & ROW_MASK) << ((19 - row) * 21)
        return board

    def mirror(self):
        board = Bitboard()
        for col in range(20):
            board |= ((self >> col) & COLUMN_MASK) << (19 - col)
        return board

    def mirror_diagonal(self):
        board = Bitboard()
        for x in range(20):
            for y in range(20):
                if self.check_bit(x + y * 21):
                    board.flip_bit(y + x * 21)
        return board

    def rotate_left(self):
        return self.mirror_diagonal().flip()

    def rotate_right(self):
        return self.mirror_diagonal().mirror()

    @staticmethod
    def with_piece(to, shape_index):
        return Bitboard(fields=PIECE_SHAPES[shape_index] << to)

    @staticmethod
    def from_parts(one, two, three, four):
        return Bitboard(one << 384 | two << 256 | three << 128 | four)

    def clone(self):
        return Bitboard(self.fields)

    def neighbours(self):
        return (self << 1 | self >> 1 | self >> 21 | self << 21) & VALID_FIELDS

    def diagonal_neighbours(self):
        return (self << 22 | self >> 22 | self >> 20 | self << 20) & VALID_FIELDS

    def __invert__(self):
        return Bitboard(self.fields ^ 13407807929942597099574024998205846127479365820592393377723561443721764030073546976801874298166903427690031858186486050853753882811946569946433649006084095)

    def __rshift__(self, n):
        return Bitboard(fields=self.fields >> n)

    def __lshift__(self, n):
        return Bitboard(fields=self.fields << n)

    def __and__(self, bitboard):
        return Bitboard(self.fields & bitboard.fields)

    def __or__(self, bitboard):
        return Bitboard(self.fields | bitboard.fields)

    def __xor__(self, bitboard):
        return Bitboard(self.fields ^ bitboard.fields)

    def __repr__(self):
        string = bin(self.fields)[2:]
        string = "0" * (420-len(string)) + string
        st = ""
        for i in range(20):
            i = 19 - i
            st += (string[i*21:(i+1)*21])[::-1][:-1] + "\n"
        return st.replace("0", " .").replace("1", " 1")

    def __eq__(self, other):
        return self.fields == other.fields

class Action:
    def __init__(self, to, shape_index):
        self.piece_type = PieceType.from_shape_index(shape_index)
        self.to = to
        self.shape_index = shape_index

    def serialize(action):
        if action == None:
            return "Skip"
        for i, pi in enumerate(PIECE_TYPES):
            if pi == action.piece_type:
                piece_index = i
        return f"{action.to} {action.shape_index}"

    @staticmethod
    def deserialize(entries):
        if entries[0] == "Skip":
            return None
        entries = [int(e) for e in entries]
        shape_index = entries.pop()
        to = entries.pop()
        return Action(to, shape_index)

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
        for shape_index in range(91):
            if Bitboard.with_piece(to, shape_index) == original_board:
                return Action(to, shape_index)

        print("Can't determine action from Bitboard")
        print(original_board)

    def __eq__(self, other):
        return other != None and self.shape_index == other.shape_index and self.to == other.to

    def __repr__(self):
        return f"Set {repr(self.piece_type)} to {self.to} (X={self.to % 21} Y={(self.to - (self.to % 21)) // 21} Shape={self.shape_index})"

class Color(Enum):
    BLUE = 0
    YELLOW = 1
    RED = 2
    GREEN = 3

    def next(self):
        if self == Color.BLUE:
            return Color.YELLOW
        if self == Color.RED:
            return Color.GREEN
        if self == Color.YELLOW:
            return Color.RED
        return Color.BLUE

    def previous(self):
        if self == Color.YELLOW:
            return Color.BLUE
        if self == Color.GREEN:
            return Color.RED
        if self == Color.RED:
            return Color.YELLOW
        return Color.GREEN

    @staticmethod
    def from_ply(ply):
        return Color(ply % 4)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "BLUE (Team ONE)" if self.value == 0 else \
            "YELLOW (Team TWO)" if self.value == 1 else \
            "RED (Team ONE)" if self.value == 2 else \
            "Green (Team Two)"

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
        if self.value == 0:
            return 1
        elif self.value < 2:
            return 2
        elif self.value < 4:
            return 3
        elif self.value < 9:
            return 4
        else:
            return 5

    def __repr__(self):
        return str(self)[10:]

    @staticmethod
    def random_pentomino():
        while True:
            idx = random.randint(9, 20)
            if idx != 18:
                return PIECE_TYPES[idx]

    @staticmethod
    def from_shape_index(shape_index):
        if shape_index == 0: return PieceType.Monomino
        if shape_index < 3: return PieceType.Domino
        if shape_index < 5: return PieceType.ITromino
        if shape_index < 7: return PieceType.ITetromino
        if shape_index < 9: return PieceType.IPentomino
        if shape_index == 9: return PieceType.OTetromino
        if shape_index == 10: return PieceType.XPentomino
        if shape_index < 15: return PieceType.LTromino
        if shape_index < 23: return PieceType.LTetromino
        if shape_index < 31: return PieceType.LPentomino
        if shape_index < 35: return PieceType.TPentomino
        if shape_index < 39: return PieceType.TTetromino
        if shape_index < 43: return PieceType.ZTetromino
        if shape_index < 47: return PieceType.ZPentomino
        if shape_index < 51: return PieceType.UPentomino
        if shape_index < 59: return PieceType.FPentomino
        if shape_index < 63: return PieceType.WPentomino
        if shape_index < 71: return PieceType.NPentomino
        if shape_index < 75: return PieceType.VPentomino
        if shape_index < 83: return PieceType.PPentomino
        if shape_index < 92: return PieceType.YPentomino
        raise ValueError(f"Invalid shape index: {shape_index}")

class GameState:
    def __init__(self):
        self.ply = 0
        self.skipped = 0
        self.board = [Bitboard() for _ in range(4)]
        self.start_piece_type = PieceType.random_pentomino()
        self.pieces_left = [[True] * 4 for _ in range(21)]
        self.monomino_placed_last = [False] * 4
        self.current_color = Color.BLUE

    def do_action(self, action):
        if action == None:
            self.current_color = Color.next(self.current_color)
            self.ply += 1
            self.skipped = ((self.skipped & 0b1111) | self.skipped << 4) | (1 << self.current_color.value)
            return
        piece = Bitboard.with_piece(action.to, action.shape_index)
        self.pieces_left[action.piece_type.value][self.current_color.value] = False
        self.board[self.current_color.value] ^= piece
        self.monomino_placed_last[self.current_color.value] = action.piece_type == PieceType.Monomino
        self.current_color = Color.next(self.current_color)
        self.ply += 1

    def undo_action(self, action):
        self.ply -= 1
        self.skipped >>= 4
        self.current_color = Color.previous(self.current_color)
        if action == None: return
        current_color = self.current_color.value
        piece = Bitboard.with_piece(action.to, action.shape_index)
        self.pieces_left[action.piece_type.value][self.current_color.value] = True
        self.board[self.current_color.value] ^= piece

    def get_possible_actions(self):
        action_list = []
        own_fields = self.board[self.current_color.value]
        other_fields = (self.board[0] | self.board[1] | self.board[2] | self.board[3]) & ~own_fields
        legal_fields = ~(own_fields | other_fields | own_fields.neighbours()) & VALID_FIELDS
        placement_fields = own_fields.diagonal_neighbours() & legal_fields if self.ply > 3 else START_FIELDS & ~other_fields

        for p in PIECE_TABLE:
            if self.pieces_left[p[0].value][self.current_color.value]:
                candidates = placement_fields.clone()
                while candidates.fields != 0:
                    to = candidates.trailing_zeros()
                    candidates.flip_bit(to)
                    shape_index = p[2]
                    for offsets in p[1]:
                        for offset in offsets:
                            if to >= offset:
                                piece = Bitboard.with_piece(to - offset, shape_index)
                                if piece & legal_fields == piece:
                                    action_list.append(Action(to - offset, shape_index))
                        shape_index += 1

        if self.pieces_left[PieceType.Monomino.value][self.current_color.value]:
            while placement_fields.fields != 0:
                to = placement_fields.trailing_zeros()
                placement_fields.flip_bit(to)
                action_list.append(Action(to, 0))

        if self.ply < 4:
            action_list = [action for action in action_list if action.piece_type == self.start_piece_type]
        return action_list if len(action_list) != 0 else [None]

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

    def piece_info_to_int(self):
        info = 0
        for player_index in range(4):
            if self.monomino_placed_last[player_index]:
                info |= 1 << player_index
            for i in range(21):
                if self.pieces_left[i][player_index]:
                    info |= 1 << (i + 21 * player_index + 4)
        info |= self.start_piece_type.value << 110
        return info

    @staticmethod
    def from_fen(fen):
        state = GameState()
        entries = [int(entry) for entry in fen.split(" ")]
        assert len(entries) >= 18
        state.ply = entries[0] & 0b11111111
        state.skipped = entries[0] >> 8
        for b in range(4):
            state.board[b].fields = entries[b * 4 + 1] << 384 | entries[b * 4 + 2] << 256 | entries[b * 4 + 3] << 128 | entries[b * 4 + 4]
        state.current_color = Color(state.ply % 4)
        state.skipped = entries[17] >> 120
        for player_index in range(4):
            state.monomino_placed_last[player_index] = (1 << player_index) & entries[17] != 0
            for i in range(21):
                state.pieces_left[i][player_index] = entries[17] & 1 << (i + 21 * player_index + 4) != 0
        start_piece_index = entries[17] >> 110 & 31
        state.start_piece_type = PIECE_TYPES[start_piece_index]
        return state

    def to_fen(self):
        fen = f"{self.ply | self.skipped << 8} "
        for board_index in range(4):
            for part in self.board[0].to_parts():
                fen += f"{part} "
        return fen + str(self.piece_info_to_int())

    @staticmethod
    def random(n=8):
        state = GameState()
        for _ in range(n):
            state.do_action(random.choice(state.get_possible_actions()))
        return state

    def __repr__(self):
        string = "╔" + "═" * 40 + "╗\n" + f"║ {self.current_color} Turn: {self.ply} Score: {self.game_result()}"
        string += " " * (84 - len(string)) + "║\n" + "╠" + "═" * 40 + "╣"
        for y in range(20):
            string += "\n║"
            for x in range(20):
                field_index = xy_to_bit_index(x, y)
                bit = 1 << field_index
                for i in range(4):
                    if self.board[i].fields & bit != 0:
                        string += ["🟦", "🟨", "🟥", "🟩"][i]
                        break
                else:
                    string += "▪ "
            string += "║"
        string += "\n╚" + "═" * 40 + "╝"
        return string

def bit_index_to_xy(bit_index):
    x = bit_index % 21
    y = (bit_index - x) // 21
    return x, y

def xy_to_bit_index(x, y):
    return x + y * 21

VALID_FIELDS = Bitboard(fields=1353841978519651780606181823587055014201997103708438138826768745134664492555299896889475908923884339705591950360690671800549375)
START_FIELDS = Bitboard(fields=1 << 418 | 1 << 399 | 1 | 1 << 19)
ROW_MASK = Bitboard(1048575)
COLUMN_MASK = Bitboard.from_parts(
    32768,
    5316914518442072874470106890883956736,
    21267658073768291497880427563535826944,
    85070632295073165991521710254143307777
)
PIECE_SHAPES = [
    1,
    3,
    2097153,
    7,
    4398048608257,
    15,
    9223376434903384065,
    31,
    19342822337210501698682881,
    6291459,
    8796107702274,
    6291457,
    2097155,
    4194307,
    6291458,
    4398048608259,
    8796097216515,
    13194143727618,
    13194141630465,
    14680065,
    2097159,
    8388615,
    14680068,
    16777231,
    2097167,
    31457281,
    31457288,
    9223376434903384067,
    27670120508612935681,
    18446752869806768131,
    27670124906661543938,
    8796097216519,
    30786329772034,
    4398061191169,
    17592200724484,
    4194311,
    14680066,
    4398052802561,
    8796099313666,
    6291462,
    12582915,
    4398052802562,
    8796099313665,
    17592200724481,
    4398061191172,
    13194143727622,
    26388283260931,
    10485767,
    14680069,
    13194141630467,
    13194143727619,
    13194152116226,
    26388285358082,
    8796099313670,
    8796105605123,
    8796107702276,
    8796107702273,
    17592200724482,
    4398061191170,
    26388285358081,
    13194152116228,
    17592198627331,
    4398052802566,
    9223385230998503426,
    18446757267851182081,
    9223376434907578370,
    18446752869808865281,
    14680076,
    25165831,
    29360131,
    6291470,
    4398048608263,
    30786333966340,
    17592194433031,
    30786327674881,
    4398052802563,
    8796099313667,
    14680067,
    6291463,
    12582919,
    14680070,
    13194145824770,
    13194145824769,
    9223376434907578369,
    9223385230996406273,
    18446757267853279234,
    18446752869808865282,
    8388623,
    4194319,
    31457284,
    31457282
]

PIECE_TYPES = [
    PieceType.Monomino,
    PieceType.Domino,
    PieceType.ITromino,
    PieceType.LTromino,
    PieceType.ITetromino,
    PieceType.LTetromino,
    PieceType.TTetromino,
    PieceType.OTetromino,
    PieceType.ZTetromino,
    PieceType.FPentomino,
    PieceType.IPentomino,
    PieceType.LPentomino,
    PieceType.NPentomino,
    PieceType.PPentomino,
    PieceType.TPentomino,
    PieceType.UPentomino,
    PieceType.VPentomino,
    PieceType.WPentomino,
    PieceType.XPentomino,
    PieceType.YPentomino,
    PieceType.ZPentomino
]

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

if __name__ == "__main__":
    state = GameState()
    while not state.is_game_over():
        print(state.to_fen())
        possible_actions = state.get_possible_actions()
        print(possible_actions)
        action = random.choice(possible_actions)
        print(action)
        state.do_action(action)
        print(state)
    print(state.game_result())

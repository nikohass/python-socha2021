
class Bitboard:
    def __init__(self, fields=0):
        self.fields = fields

    def flip_bit(self, bit_idx):
        self.fields ^= 1 << bit_idx

    def count_ones(self):
        ones = 0
        board_copy = self.fields
        bit = 1
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

    @staticmethod
    def with_piece(to, shape_index):
        piece_shape = PIECE_SHAPES[shape_index]
        return Bitboard(fields=piece_shape << to)
    
    def neighbours(self):
        return (self << 1 | self >> 1 | self >> 21 | self << 21) & VALID_FIELDS

    def diagonal_neighbours(self):
        return (self << 22 | self >> 22 | self >> 20 | self << 20) & VALID_FIELDS

    def neighbours_in_direction(self, d):
        if d == "UP":
            return Bitboard(self.fields << 21) & VALID_FIELDS
        if d == "DOWN":
            return Bitboard(self.fields >> 21) & VALID_FIELDS
        if d == "LEFT":
            return Bitboard(self.fields << 1) & VALID_FIELDS
        if d == "RIGHT":
            return Bitboard(self.fields >> 1) & VALID_FIELDS
        raise

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
            st += (string[i*21:(i+1)*21])[::-1] + "\n"
        return st

    def __eq__(self, other):
        return self.fields == other.fields

    def copy(self):
        return Bitboard(fields=self.fields)

VALID_FIELDS = Bitboard(fields=1353841978519651780606181823587055014201997103708438138826768745134664492555299896889475908923884339705591950360690671800549375)
START_FIELDS = Bitboard(fields=1 << 418 | 1 << 399 | 1 | 1 << 19)
PIECE_SHAPES = [
    1,                          # Monomino
    3,                          # Domino horizontal
    2097153,                    # Domion vertical
    7,                          # I-Tromino horizontal
    4398048608257,              # I-Tromino vertical
    15,                         # I-Tetromino horizontal
    9223376434903384065,        # I-Tetromino vertical
    31,                         # I-Pentomino horizontal
    19342822337210501698682881, # I-Pentomino vertical
    6291459,                    # O-Tetromino
    4398053851137,              # X-Pentomino
    6291457,                    # L-Tromino
    2097155,
    4194307,
    6291458,
    4398048608259, # L-Tetromino
    8796097216515,
    13194143727618,
    13194141630465,
    14680065,
    2097159,
    8388615,
    14680068,
    16777231, # L-Pentomino
    2097167,
    31457281,
    31457288,
    9223376434903384067,
    27670120508612935681,
    18446752869806768131,
    27670124906661543938,
    8796097216519, # T-Pentomino
    30786329772034,
    4398061191169,
    17592200724484,
    4194311, # T-Tetromino
    14680066,
    4398052802561,
    8796099313666,
    6291462, # Z-Tetromino
    12582915,
    4398052802562,
    8796099313665,
    17592200724481, # Z-Pentomino
    4398061191172,
    13194143727622,
    26388283260931,
    10485767, # U-Pentomino
    14680069,
    13194141630467,
    13194143727619,
    13194152116226, # F-Pentomino
    26388285358082,
    8796099313670,
    8796105605123,
    8796107702276,
    8796107702273,
    17592200724482,
    4398061191170,
    26388285358081, # W-Pentomino
    13194152116228,
    17592198627331,
    4398052802566,
    9223385230998503426, # N-Pentomino
    18446757267851182081,
    9223376434907578370,
    18446752869808865281,
    14680076,
    25165831,
    29360131,
    6291470,
    4398048608263, # V-Pentomino
    30786333966340,
    17592194433031,
    30786327674881,
    4398052802563, # P-Pentomino
    8796099313667,
    14680067,
    6291463,
    12582919,
    14680070,
    13194145824770,
    13194145824769,
    9223376434907578369, # Y-Pentomino
    9223385230996406273,
    18446757267853279234,
    18446752869808865282,
    8388623,
    4194319,
    31457284,
    31457282
]
DIRECTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]

def mirror(d):
    if d == "UP":
        return "DOWN"
    if d == "DOWN":
        return "UP"
    if d == "LEFT":
        return "RIGHT"
    if d == "RIGHT":
        return "LEFT"

def anticlockwise(d):
    if d == "LEFT":
        return "DOWN"
    if d == "UP":
        return "LEFT"
    if d == "RIGHT":
        return "UP"
    if d == "DOWN":
        return "RIGHT"

def clockwise(d):
    if d == "LEFT":
        return "UP"
    if d == "UP":
        return "RIGHT"
    if d == "RIGHT":
        return "DOWN"
    if d == "DOWN":
        return "LEFT"

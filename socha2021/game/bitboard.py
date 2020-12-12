
class Bitboard:
    def __init__(self, fields=0):
        self.fields = fields

    def flip_bit(self, bit_idx):
        self.fields ^= 1 << bit_idx

    def check_bit(self, bit_idx):
        return self.fields & (1 << bit_idx) != 0

    def print_parts(self):
        print("one  ", self.fields >> 384 & 340282366920938463463374607431768211455)
        print("two  ", self.fields >> 256 & 340282366920938463463374607431768211455)
        print("three", self.fields >> 128 & 340282366920938463463374607431768211455)
        print("four ", self.fields & 340282366920938463463374607431768211455)

    def to_parts(self):
        return (self.fields >> 384 & 340282366920938463463374607431768211455,
            self.fields >> 256 & 340282366920938463463374607431768211455,
            self.fields >> 128 & 340282366920938463463374607431768211455,
            self.fields & 340282366920938463463374607431768211455)

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
        string = "." * (420-len(string)) + string
        st = ""
        for i in range(20):
            st += (string[i*21:(i+1)*21])[::-1][:-1] + "\n"
        return st.replace("0", ".")

    def __eq__(self, other):
        return self.fields == other.fields

    def copy(self):
        return Bitboard(fields=self.fields)

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

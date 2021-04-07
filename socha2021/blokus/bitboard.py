
class Bitboard:
    def __init__(self, fields=0):
        self.fields = fields

    def flip_bit(self, bit_index: int):
        self.fields ^= 1 << bit_index

    def check_bit(self, bit_index: int) -> bool:
        return self.fields & (1 << bit_index) != 0

    def count_ones(self) -> int:
        ones = 0
        bit = 1
        board_copy = self.fields
        while board_copy != 0:
            if bit & board_copy != 0:
                ones += 1
                board_copy ^= bit
            bit <<= 1
        return ones

    def trailing_zeros(self) -> int:
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

    def get_start_corner(self) -> int:
        if self.check_bit(0):
            return 0
        elif self.check_bit(19):
            return 1
        elif self.check_bit(399):
            return 2
        else:
            return 3

    @staticmethod
    def with_piece(destination, shape: int):
        return Bitboard(PIECE_SHAPES[shape] << destination)

    @staticmethod
    def from_parts(a: int, b: int, c: int, d: int):
        return Bitboard(a << 384 | b << 256 | c << 128 | d)

    def clone(self):
        return Bitboard(self.fields)

    def neighbours(self):
        return (self << 1 | self >> 1 | self >> 21 | self << 21) & VALID_FIELDS

    def diagonal_neighbours(self):
        return (self << 22 | self >> 22 | self >> 20 | self << 20) & VALID_FIELDS

    def __iter__(self):
        return self

    def __next__(self) -> int:
        bit_index = self.trailing_zeros()
        if bit_index == 512:
            raise StopIteration
        self.flip_bit(bit_index)
        return bit_index

    def __invert__(self):
        return Bitboard(self.fields ^ 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)

    def __rshift__(self, n):
        return Bitboard(self.fields >> n)

    def __lshift__(self, n):
        return Bitboard(self.fields << n)

    def __and__(self, other):
        return Bitboard(self.fields & other.fields)

    def __or__(self, other):
        return Bitboard(self.fields | other.fields)

    def __xor__(self, other):
        return Bitboard(self.fields ^ other.fields)

    def __eq__(self, other):
        return self.fields == other.fields

    def to_parts(self) -> tuple:
        return (
            self.fields >> 384 & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            self.fields >> 256 & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            self.fields >> 128 & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            self.fields & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        )

    def __repr__(self):
        string = bin(self.fields)[2:]
        string = "0" * (420-len(string)) + string
        st = ""
        for i in range(20):
            i = 19 - i
            st += (string[i*21:(i+1)*21])[::-1][:-1] + "\n"
        return st.replace("0", " .").replace("1", " 1")

    def print_parts(self):
        a, b, c, d = self.to_parts()
        print(f"Bitboard({a}, {b}, {c}, {d})")

    def to_fen(self) -> str:
        a, b, c, d = self.to_parts()
        return f"{a} {b} {c} {d}"

    def get_pieces(self):
        board = self.clone()
        actions = []
        while board.fields != 0:
            piece = Bitboard(1 << board.trailing_zeros())
            for _ in range(5):
                piece |= piece.neighbours() & board
            board ^= piece
            actions.append(Action.from_bitboard(piece))
        return actions

def convert(*args):
    if len(args) == 2:
        x, y = args
        return x + y * 21
    bit_index = args[0]
    x = bit_index % 21
    y = (bit_index - x) // 21
    return x, y

VALID_FIELDS = Bitboard(1353841978519651780606181823587055014201997103708438138826768745134664492555299896889475908923884339705591950360690671800549375)
START_FIELDS = Bitboard(1 << 418 | 1 << 399 | 1 | 1 << 19)
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

from enum import Enum

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
        return ["🟦", "🟨", "🟥", "🟩"][self.value]

from blokus.gamestate import *
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import numpy as np

L0_SIZE = 13
L1_SIZE = 1

class Tuning:
    def __init__(self):
        self.model = Sequential(
            [
                Dense(L1_SIZE, input_shape=(L0_SIZE,), activation=None),
            ]
        )
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(1e-4),
            loss="mean_squared_error",
            metrics=['accuracy']
        )
        self.model.build()
        print(self.model.summary())

    def train(self, X, Y, epochs):
        self.model.fit(X, Y, epochs=epochs)

    def print_weights(self):
        print("Weights:")
        weights = self.model.get_weights()
        for w in weights:
            if len(w.shape) == 1:
                print(list(w))
            else:
                l = []
                for i in w:
                    a = list(i)
                    if len(a) == 1:
                        l.append(a[0])
                    else:
                        l.append(a)
                print(l)
            print()

def load_dataset(path):
    X = []
    Y = []
    with open(path, "r") as dataset_file:
        for i, line in enumerate(dataset_file):
            print(i)
            #if i > 2000: break
            try:
                for x, y in line_to_examples(line):
                    X.append(x)
                    Y.append(y)
            except KeyboardInterrupt:
                break
            except:
                print(line)
    return np.array(X), np.array(Y)

def line_to_examples(line):
    state = GameState(line)
    inp = np.zeros(shape=(L0_SIZE))
    current_color = state.current_color.value
    next_opponent_color = (current_color + 1) & 0b11
    second_color = (current_color + 2) & 0b11
    last_opponent_color = (current_color + 3) & 0b11
    occupied = state.get_occupied_fields()
    placement_fields = []
    for color in range(4):
        current_color_fields = state.board[color]
        other_colors_fields = occupied & ~current_color_fields
        legal_fields = ~(occupied | current_color_fields.neighbours()) & VALID_FIELDS
        placement_fields.append(current_color_fields.diagonal_neighbours() & legal_fields if state.ply > 3 else START_FIELDS & ~other_colors_fields)
    reachable_fields = []
    for color in range(4):
        reachable = placement_fields[color]
        unreachable = state.board[color].neighbours() | occupied
        for _ in range(4):
            reachable |= reachable.neighbours() & ~unreachable
        reachable_fields.append(reachable)
    leaks = []
    for color in range(4):
        leaks.append(reachable_fields[color] & (placement_fields[color] & occupied.neighbours() & ~(occupied | state.board[color].neighbours())).diagonal_neighbours()& occupied.neighbours())
    opponent_placement_fields = placement_fields[next_opponent_color] | placement_fields[last_opponent_color]
    opponent_reachable_fields = reachable_fields[next_opponent_color] | reachable_fields[last_opponent_color]
    k = reachable_fields[current_color] & (occupied & ~state.board[current_color]).neighbours() & ~(occupied & ~state.board[current_color]).diagonal_neighbours()

    entries = line.split()[18:]
    assert len(entries) % 2 == 0
    max_value = 0
    min_value = 1
    for i in range(len(entries) // 2):
        index = i * 2
        value = float(entries[index + 1])
        if value < min_value:
            min_value = value
        if value > max_value:
            max_value = value
    for i in range(len(entries) // 2):
        index = i * 2
        action = Action.deserialize(int(entries[index]))
        value = (float(entries[index + 1]) - min_value) / (max_value - min_value)
        shape = action.shape
        destination = action.destination
        piece_type = PieceType.from_shape(shape)
        if state.ply < 8 and piece_type.piece_size() < 5:
            continue
        piece = Bitboard.with_piece(destination, shape)
        new_placement_fields = piece.diagonal_neighbours() & ~(piece | state.board[current_color]).neighbours() & ~occupied
        if state.ply < 8:
            min_distance_to_center = 100
            for field in Bitboard.with_piece(destination, shape):
                x, y = convert(field)
                distance_to_center = ((x - 9.5) ** 2 + (y - 9.5) ** 2) ** 0.5
                min_distance_to_center = min(min_distance_to_center, distance_to_center)
        else:
            min_distance_to_center = 0
        inp = np.array([
            piece.count_ones(),
            (piece & leaks[current_color]).count_ones(),
            (piece & leaks[current_color].diagonal_neighbours() & ~(opponent_reachable_fields | occupied)).count_ones(),
            (piece & leaks[next_opponent_color]).diagonal_neighbours().count_ones(),
            (piece & leaks[last_opponent_color]).diagonal_neighbours().count_ones(),
            (piece & opponent_placement_fields).count_ones(),
            (piece & opponent_placement_fields.diagonal_neighbours()).count_ones(),
            (new_placement_fields & reachable_fields[next_opponent_color]).count_ones(),
            (new_placement_fields & reachable_fields[last_opponent_color]).count_ones(),
            new_placement_fields.count_ones(),
            (piece & placement_fields[second_color]).count_ones(),
            (piece & k).count_ones(),
            min_distance_to_center,
        ], dtype=np.float32)
        yield inp, value

X, Y = load_dataset("datasets/dataset_0.txt")
print(X.shape, Y.shape)
nn = Tuning()
nn.train(X, Y, 10)
nn.print_weights()

import os
import struct
import numpy as np
import random, copy
import tensorflow as tf
from copy import deepcopy
from blokus.gamestate import *
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, Flatten

INPUT_SHAPE = (20, 20, 5)

def state_to_input(state):
    inp = np.zeros(shape=INPUT_SHAPE)
    board = Bitboard()
    for action in state.get_possible_actions():
        board |= Bitboard.with_piece(action.destination, action.shape)
    for field_index in board:
        x, y = convert(field_index)
        inp[x][y][4] = 1
    index = 0
    for color in [(state.current_color.value + i) % 4 for i in range(4)]:
        for field_index in state.board[color].clone():
            x, y = convert(field_index)
            inp[x][y][index] = 1.0
        index += 1
    return inp

def to_example(line):
    state = GameState(line)
    if state.ply < 4:
        return None, None
    r = Rotation.from_state(state)
    r.rotate_state(state)
    entries = line.split()[18:]

    sum_values = np.zeros(shape=(400), dtype=np.float16)
    n = np.zeros(shape=(400), dtype=np.float16)
    for i in range(len(entries) // 2):
        action = Action.deserialize(int(float(entries[i])))
        value = float(entries[i + 1])
        if value > 1: continue
        board = Bitboard.with_piece(action.destination, action.shape)
        for bit_index in board:
            x, y = convert(bit_index)
            index = x + y * 20
            sum_values[index] += value
            n[index] += 1
    """
    zeros = n == 0
    n[zeros] = 1000
    y = sum_values / n
    y -= min(0, y.min() - 0.1)
    y[zeros] = 0
    max_value = y.max()
    #if max_value == 0:
    #    return None, None
    y /= max_value
    """
    empty = n == 0
    not_empty = n != 0
    if not any(not_empty):
        return None, None
    n[empty] = 1
    y = sum_values / n
    y -= y[not_empty].min()
    max = y.max()
    if max == 0:
        return None, None
    y /= max
    y[empty] = 0
    y = r.rotate_y(y)

    if np.isnan(y).any() or y[not_empty].min() == 1:
        return None, None
    return state_to_input(state), y

def load_datasets(datasets, limit=None):
    for dataset_path in datasets:
        if not os.path.exists(dataset_path):
            print(f"{dataset_path} does not exist")
            raise
    X = []
    Y = []
    i = 0
    for dataset_path in datasets:
        with open(dataset_path, "r") as file:
            for line in file:
                try:
                    x, y = to_example(line)
                    if x is None:
                        continue
                    X.append(x)
                    Y.append(y)
                    i += 1
                    if i % 500 == 0:
                        print(i)
                    if limit != None and i > limit:
                        break
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(e, line)
    return np.array(X), np.array(Y)

class Rotation:
    def __init__(self, top_left_corner: int):
        self.top_left_corner = top_left_corner

    def rotate_bitboard(self, bitboard: Bitboard) -> Bitboard:
        if self.top_left_corner == 1:
            bitboard = bitboard.mirror()
        elif self.top_left_corner == 2:
            bitboard = bitboard.flip()
        elif self.top_left_corner == 3:
            bitboard = bitboard.rotate_left().rotate_left()
        return bitboard

    def rotate_state(self, state: GameState):
        for color, board in enumerate(state.board):
            state.board[color] = self.rotate_bitboard(board)

    def rotate_action(self, action: Action) -> Action:
        if action == None:
            return None
        piece_type = action.piece_type
        action = Action.from_bitboard(
            self.rotate_bitboard(Bitboard.with_piece(action.destination, action.shape))
        )
        action.piece_type = piece_type
        return action

    def rotate_y(self, y):
        y = np.array(y[:400]).reshape(20, 20)
        if self.top_left_corner == 1:
            y = np.fliplr(y)
        elif self.top_left_corner == 2:
            y = np.flipud(y)
        elif self.top_left_corner == 3:
            y = np.rot90(y, 2)
        return y.flatten()

    @staticmethod
    def from_state(state: GameState):
        current_color = state.current_color.value
        top_left_corner = 3
        for corner, field in enumerate([0, 19, 399]):
            if state.board[current_color].check_bit(field):
                top_left_corner = corner
                break
        return Rotation(top_left_corner)

class NeuralNetwork:
    def __init__(self):
        self.model = Sequential(
            [
                Conv2D(128, (7, 7), activation="relu", input_shape=(INPUT_SHAPE), padding="same"),
                Conv2D(32, (5, 5), activation="relu", padding="same"),
                Conv2D(32, (3, 3), activation="relu", padding="same"),
                Conv2D(32, (3, 3), activation="relu", padding="same"),
                Conv2D(1, (3, 3), activation="relu", padding="same"),
                Flatten(),
                Dense(400, activation="relu"),
                Dense(400, activation="sigmoid")
            ]
        )
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(1e-4),
            loss="mean_squared_error",
            metrics=['accuracy']
        )
        self.model.build(input_shape=INPUT_SHAPE)
        self.model.summary()

    def save_weights(self, filename: str):
        print(f"saving weights to \"{filename}\"", end=" ")
        byte_array = bytearray()
        weights = self.model.get_weights()
        for layer in weights:
            if len(layer.shape) == 1:
                for w in layer:
                    byte_array += struct.pack("f", w)
            elif len(layer.shape) == 4:
                for i in layer:
                    for j in i:
                        for k in j:
                            for w in k:
                                byte_array += struct.pack("f", w)
            elif len(layer.shape) == 2:
                for l in layer:
                    for f in l:
                        byte_array += struct.pack("f", f)
        with open(filename, "wb") as checkpoint_file:
            checkpoint_file.write(byte_array)
        print("Done")

    def load_weights(self, filename: str):
        print(f"loading weights from \"{filename}\" ", end="")
        with open(filename, "rb") as checkpoint_file:
            byte_array = checkpoint_file.read()
        weights = self.model.get_weights()
        index = 0
        for layer in weights:
            if len(layer.shape) == 1:
                for i in range(len(layer)):
                    layer[i] = struct.unpack('f', byte_array[index:index+4])[0]
                    index += 4
            elif len(layer.shape) == 4:
                for i in layer:
                    for j in i:
                        for k in j:
                            for w in range(len(k)):
                                k[w] = struct.unpack('f', byte_array[index:index+4])[0]
                                index += 4
            elif len(layer.shape) == 2:
                for i in range(layer.shape[0]):
                    for j in range(layer.shape[1]):
                        layer[i][j] = struct.unpack('f', byte_array[index:index+4])[0]
                        index += 4
        self.model.set_weights(weights)
        assert len(byte_array) == index
        print("Done")

    def pick_action(self, state: GameState) -> tuple:
        state = deepcopy(state)
        rotation = Rotation.from_state(state)
        rotation.rotate_state(state)
        possible_actions = state.get_possible_actions()
        if possible_actions[0] == None:
            return None, -1.0
        inp = state_to_input(state)
        out = self.model.predict(np.array([inp]))[0]
        #plt.imshow(np.array(list(out)[:400]).reshape(20, 20))
        #plt.show()
        #print(out[-1])r
        #out = rotation.rotate_y_back(out)
        #print(state)
        #plt.imshow(out.reshape(20, 20), cmap='jet', vmin=0., vmax=1.)
        #plt.show()
        best_action = possible_actions[0]
        best_score = -100.0
        for action in possible_actions:
            score = 0
            piece = Bitboard.with_piece(action.destination, action.shape)
            for field_index in piece:
                x, y = convert(field_index)
                score += out[(x + y * 20)]
            if score > best_score:
                best_score = score
                best_action = action
        return rotation.rotate_action(best_action), best_score

    def train(self, X, Y, epochs):
        self.model.fit(X, Y, epochs=epochs)

if __name__ == "__main__":
    nn = NeuralNetwork()
    checkpoint = 0

    #checkpoint = max([int(filename) for filename in os.listdir("checkpoints")])
    #nn.load_weights(f"checkpoints/{checkpoint}")

    X, Y = load_datasets(
        [
            "datasets/test_dataset.txt",
            "datasets/dataset_0.txt",
        ]
    )
    print(X.shape, Y.shape)
    while True:
        nn.train(X, Y, 25)
        nn.save_weights(f"checkpoints/{checkpoint}")
        checkpoint += 1

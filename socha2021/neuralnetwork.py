import os
import struct
from blokus import *
from utils import *
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential

class NeuralNetwork:
    def __init__(self, load_checkpoint, checkpoint_dir="checkpoints", model=None, learning_rate=1e-5,
                input_dims=INPUT_DIMS, output_dims=OUTPUT_DIMS):
        self.model = Sequential(
            [
                Dense(INPUT_DIMS, activation="relu"),
                Dense(1024, activation="relu"),
                Dense(1024, activation="relu"),
                Dense(1024, activation="relu"),
                Dense(1024, activation="relu"),
                Dense(1024, activation="relu"),
                Dense(OUTPUT_DIMS, activation="sigmoid"),
            ]
        ) if model == None else model
        self.model.compile(
            loss='categorical_crossentropy',
            optimizer=tf.keras.optimizers.Adam(learning_rate),
            metrics=['accuracy'],
        )
        self.checkpoint_dir = checkpoint_dir
        self.model.build((1, INPUT_DIMS))
        self.checkpoint_index = 0
        if type(load_checkpoint) == str:
            self.load_checkpoint(load_checkpoint)
        elif load_checkpoint:
            self.load_latest_checkpoint()

    def load_checkpoint(self, checkpoint_path):
        print(f"loading checkpoint \"{checkpoint_path}\"...")
        with open(checkpoint_path, "rb") as file:
            byte_array = file.read()
        weights = self.model.get_weights()
        index = 0
        for layer in weights:
            shape = layer.shape
            if len(shape) == 1:
                # biases
                for i in range(shape[0]):
                    layer[i] = struct.unpack('f', byte_array[index*4:index*4+4])[0]
                    index += 1
            else:
                # weights
                for i in range(shape[0]):
                    for j in range(shape[1]):
                        layer[i][j] = struct.unpack('f', byte_array[index*4:index*4+4])[0]
                        index += 1

        #print(index, len(byte_array) // 4)
        assert index == len(byte_array) // 4
        self.model.set_weights(weights)

    def load_latest_checkpoint(self):
        checkpoints = [int(filename.strip("save")) for filename in os.listdir(self.checkpoint_dir)]
        if len(checkpoints) == 0:
            print("No checkpoint available")
            return
        self.checkpoint_index = max(checkpoints) + 1
        checkpoint_path = f"{self.checkpoint_dir}/save{self.checkpoint_index - 1}"
        self.load_checkpoint(checkpoint_path)

    def save_checkpoint(self):
        filename = f"{self.checkpoint_dir}/save{self.checkpoint_index}"
        print(f"saving checkpoint \"{filename}\"...")
        weights = self.model.get_weights()
        byte_array = bytearray()
        for layer in weights:
            if len(layer.shape) == 1:
                # biases
                for f in layer:
                    byte_array += struct.pack("f", f)
            else:
                # weights
                for l in layer:
                    for f in l:
                        byte_array += struct.pack("f", f)
        with open(filename, "wb") as checkpoint_file:
            checkpoint_file.write(byte_array)
        self.checkpoint_index += 1

    def predict_single(self, x):
        return self.model.predict(np.array([x]))[0]

    def predict_batch(self, x):
        return self.model.predict(x)

    def train(self, X, Y, epochs, batch_size=None, verbose=1):
        self.model.fit(X, Y, batch_size=batch_size, verbose=verbose, epochs=epochs)

    def pick_action(self, state: GameState, epsilon=0):
        rotation = Rotation.from_state(state)
        rotation.rotate_state(state)
        possible_actions = state.get_possible_actions()
        if possible_actions[0] == None: return None, [np.zeros(400)] # Skip
        input_array = state_to_array(state)
        output_array = self.predict_single(input_array) + np.random.random(400) * epsilon
        best_action = Bitboard.with_piece(possible_actions[0].to, possible_actions[0].shape_index)
        best_score = -100_000
        for action in possible_actions:
            action_score = 0
            action_board = Bitboard.with_piece(action.to, action.shape_index)
            while action_board.fields != 0:
                bit_index = action_board.trailing_zeros()
                action_board.flip_bit(bit_index)
                x = bit_index % 21
                y = (bit_index - x) // 21
                action_score += output_array[(x + y * 20)]
            if action_score > best_score:
                best_score = action_score
                best_action = action
        return rotation.rotate_action(best_action), [output_array]

def check_gpus():
    gpus = tf.config.list_physical_devices('GPU')
    if len(gpus) == 0:
        input("No GPU available. Press enter to continue with the CPU.")
    else:
        print(gpus)

if __name__ == "__main__":
    import os

    check_gpus()
    nn = NeuralNetwork(True)
    nn.model.summary()
    #datasets = ["datasets/" + filename for filename in os.listdir("datasets/")]
    datasets = "datasets/pvs2000ms.txt"
    X, Y = load_datasets(datasets)

    while True:
        nn.train(X, Y, 10)
        nn.save_checkpoint()

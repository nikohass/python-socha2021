import os
import copy
from random import choice
from neuralnetwork import *

def play_game(nn):
    state = GameState()
    while not state.is_game_over():
        action, l = nn.pick_action(copy.deepcopy(state))
        state.do_action(action)
        state.do_action(choice(state.get_possible_actions()))
    return state.game_result()

def test_dataset(path):
    with open(path, "r") as file:
        for line in file:
            line = line.strip()
            print(line)
            if len(line) < 18:
                continue
            state = GameState.from_fen(line)
            action = Action.deserialize(line.split()[18:])
            rotation = Rotation.from_state(state)
            rotation.rotate_state(state)
            g.clear()
            g.draw_state(state)
            g.draw_action(rotation.rotate_bitboard(Bitboard.with_piece(action.to, action.shape_index)))
            g.update()
            input("")

if __name__ == "__main__":
    #print(test_nn())
    from gui import Gui
    g = Gui()

    nn = NeuralNetwork(True)
    while True:
        state = GameState()
        while not state.is_game_over():
            action, l = nn.pick_action(copy.deepcopy(state))
            heatmap = l[0].reshape((-1, 20))
            heatmap = heatmap / np.amax(heatmap)
            action_board = Bitboard() if action == None else Bitboard.with_piece(action.to, action.shape_index)
            g.draw_state(state)
            g.draw_action(action_board)
            g.draw_nn_output(heatmap, state.current_color.value)
            g.update()
            g.clear()
            state.do_action(action)
            #input()
            #state.do_action(choice(state.get_possible_actions()))
            #print(state)
            #input()
        print(state.game_result())

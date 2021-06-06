from neural_network import *
from random import choice
import os

checkpoint = max([int(filename) for filename in os.listdir("checkpoints")])

nn = NeuralNetwork()
nn.load_weights(f"checkpoints/{checkpoint}")

sum_results = 0
played_games = 0
while True:
    state = GameState()
    while not state.is_game_over():
        if state.ply % 2 == 0:
            action, conf = nn.pick_action(state)
            print(action, conf)
            state.do_action(action)
        else:
            state.do_action(choice(state.get_possible_actions()))
        print(state)
        input()
    #result = state.game_result()
    played_games += 1
    sum_results += (state.board[0] | state.board[2]).count_ones()
    print(sum_results / played_games)

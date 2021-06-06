import subprocess
from blokus.gamestate import *
import time
import random
from threading import Thread

def get_mcts_action(state, i=500_000):
    cmd = ["dataset.exe", "--fen", state.to_fen(), "--iterations", str(i)]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = p.stdout.readline().decode("utf-8")
        if line[:6] == "result":
            p.terminate()
            break
        else:
            print(line.strip())
    return line[7:], Action.deserialize(int(line[7:].split()[0]))

def save_data(state, line, path):
    entries = line.split()
    del entries[0]
    entries.pop()
    assert len(entries) % 2 == 0
    with open(path, "a") as file:
        string = state.to_fen()
        for entry in entries:
            string += " " + str(entry)
        file.write(string + "\n")

def play_game(path, iterations):
    state = GameState()
    while not state.is_game_over() and state.ply < 32:
        if random.random() > 0.4:
            line, action = get_mcts_action(state, i=iterations)
            save_data(state, line, path)
            state.do_action(action)
        else:
            state.do_action(random.choice(state.get_possible_actions()))
        print(state)
    print(state.game_result())

def run_thread():
    while True:
        play_game("datasets/dataset_0.txt", 300_000)    

if __name__ == "__main__":
    for _ in range(10):
        t = Thread(target=run_thread)
        t.daemon = True
        t.start()
    while True:
        time.sleep(1)

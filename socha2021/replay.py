from blokus.gamestate import *

with open("tests/log.txt", "r") as file:
    for line in file:
        index = line.find("  fen: ")
        if index == -1:
            #print(line, end="")
            continue
        input()
        state = GameState(line[index+7:])
        print(state)

for i in state.pieces_left:
    print(i[1])

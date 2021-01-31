from blokus import *
import numpy as np
import pygame

pygame.display.init()
pygame.font.init()
font = pygame.font.SysFont("arial", 30)
pygame.display.set_caption("Blokus")
COLORS = [(0, 0, 255), (255, 255, 0), (255, 0, 0), (0, 255, 0)]

class Gui:
    def __init__(self):
        self.window = pygame.display.set_mode((1200, 800))

    def clear(self):
        self.window.fill((0, 0, 0))

    def update(self):
        pygame.display.update()
        return pygame.event.get()

    def draw_state(self, state: GameState):
        pygame.draw.rect(self.window, (0, 0, 0), (0, 0, 400, 400))
        for color_index, color in enumerate(COLORS):
            board = state.board[color_index].clone()
            while board.fields != 0:
                bit_index = board.trailing_zeros()
                board.flip_bit(bit_index)
                x, y = bit_index_to_xy(bit_index)
                pygame.draw.rect(self.window, color, (x * 20 + 1, y * 20 + 1, 18, 18))

    def draw_nn_output(self, output: np.array, current_color: int):
        if output.shape == (400,):
            output = output.reshape((-1, 20))
        assert output.shape == (20, 20)
        x_offset, y_offset = [(0, 0), (400, 0), (0, 400), (400, 400)][current_color]
        for x in range(20):
            for y in range(20):
                try:
                    v = 255 * output[x][y]
                    pygame.draw.rect(self.window, (v, v, v), (x * 20 + 401 + x_offset, y * 20 + 1 + y_offset, 18, 18))
                except:
                    pass

    def draw_action(self, action):
        if type(action) == Action:
            action_board = Bitboard.with_piece(action.to, action.shape_index)
        elif type(action) == Bitboard:
            action_board = action
        while action_board.fields != 0:
            bit_index = action_board.trailing_zeros()
            action_board.flip_bit(bit_index)
            x, y = bit_index_to_xy(bit_index)
            pygame.draw.rect(self.window, (255, 255, 255), (x * 20 + 1, y * 20 + 1, 18, 18))

    def manual_evaluation(self, state: GameState, action: Action):
        self.clear()
        self.draw_state(state)
        self.draw_action(action)

        while True:
            pygame.time.delay(20)
            self.window.blit(font.render("Press left to delete, right to save", False, (255, 255, 255)), (10, 410))
            events = self.update()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        return False
                    if event.key == pygame.K_RIGHT:
                        return True

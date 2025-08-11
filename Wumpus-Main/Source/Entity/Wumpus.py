from Entity.Entity import Entity
import random
from constants import *


class Wumpus(Entity):
    def __init__(self, row, col, size: int = CELL_SIZE):
        super().__init__(row, col, WUMPUS_IMAGE, size)
    def move_random(self, board):
        # print(f"Wumpus at ({self.row}, {self.col}) is moving randomly.")  # Hidden for cleaner output
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)
        for dx, dy in directions:
            new_row = self.row + dx
            new_col = self.col + dy
            if not board.is_valid_cell(new_row, new_col):
                continue
            has_other_wumpus = False
            for w in board.Wumpus:
                if w is not self and w.row == new_row and w.col == new_col:
                    has_other_wumpus = True
                    break
            if has_other_wumpus:
                continue
            self.row = new_row
            self.col = new_col
            self.rect.x = self.col * CELL_SIZE
            self.rect.y = self.row * CELL_SIZE
            self.rect.top = self.row * CELL_SIZE + MARGIN["TOP"] + (self.row + 1) * SPACING_CELL
            self.rect.left = self.col * CELL_SIZE + MARGIN["LEFT"] + (self.col + 1) * SPACING_CELL
            board.update_stenches()
            return
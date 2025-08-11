from Entity.Entity import Entity
from constants import BREEZE_IMAGE, CELL_SIZE


class Breeze(Entity):
    def __init__(self, row, col, size: int = CELL_SIZE):
        super().__init__(row, col, BREEZE_IMAGE, size)

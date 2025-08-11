from Entity.Entity import Entity
from constants import GOLD_IMAGE, CELL_SIZE


class Gold(Entity):
    def __init__(self, row, col, size: int = CELL_SIZE):
        super().__init__(row, col, GOLD_IMAGE, size)

from Entity.Entity import Entity
from constants import STENCH_IMAGE, CELL_SIZE


class Stench(Entity):
    def __init__(self, row, col, size: int = CELL_SIZE):
        super().__init__(row, col, STENCH_IMAGE, size)

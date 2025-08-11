from Entity.Entity import Entity
from constants import PIT_IMAGE, CELL_SIZE


class Pit(Entity):
    def __init__(self, row, col, size: int = CELL_SIZE):
        super().__init__(row, col, PIT_IMAGE, size)

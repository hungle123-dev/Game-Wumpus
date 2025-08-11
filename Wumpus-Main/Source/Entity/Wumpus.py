from Entity.Entity import Entity
from constants import WUMPUS_IMAGE, CELL_SIZE


class Wumpus(Entity):
    def __init__(self, row, col, size: int = CELL_SIZE):
        super().__init__(row, col, WUMPUS_IMAGE, size)

from Entity.Entity import Entity
from constants import WALL_IMAGE, CELL_SIZE


class Wall(Entity):
    def __init__(self, row, col, size: int = CELL_SIZE):
        super().__init__(row, col, WALL_IMAGE, size)

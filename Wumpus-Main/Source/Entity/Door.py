from Entity.Entity import Entity
from constants import DOOR_IMAGE, CELL_SIZE


class Door(Entity):
    def __init__(self, row, col, size: int = CELL_SIZE):
        super().__init__(row, col, DOOR_IMAGE, size)

from Entity.Entity import Entity
from constants import ARROW_IMAGE, CELL_SIZE


class Arrow(Entity):
    def __init__(self, pos_from, pos_to, size: int = CELL_SIZE):
        image = ARROW_IMAGE[1]
        if pos_from[0] < pos_to[0]:
            image = ARROW_IMAGE[3]
        elif pos_from[0] > pos_to[0]:
            image = ARROW_IMAGE[2]
        elif pos_from[1] < pos_to[1]:
            image = ARROW_IMAGE[0]

        super().__init__(pos_to[0], pos_to[1], image, size)

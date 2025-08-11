import pygame

import utils
from constants import AGENT_IMAGE, WUMPUS_IMAGE, WUMPUS_IMAGE_KILL, PIT_IMAGE, GOLD_IMAGE, BREEZE_IMAGE, STENCH_IMAGE, \
    ARROW_IMAGE, WALL_IMAGE, CELL_IMAGE, CELL_GOLD_IMAGE


class Item(object):
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.size = 200
        if name == 'AGENT':
            self.item = utils.Utils.load_image_alpha(AGENT_IMAGE[3], 0, self.size)
        elif name == 'WUMPUS':
            self.item = utils.Utils.load_image_alpha(WUMPUS_IMAGE, 0, self.size)
        elif name == 'WUMPUS DEAD':
            self.item = utils.Utils.load_image_alpha(WUMPUS_IMAGE_KILL, 0, self.size)
        elif name == 'PIT':
            self.item = utils.Utils.load_image_alpha(PIT_IMAGE, 0, self.size)
        elif name == 'GOLD':
            self.item = utils.Utils.load_image_alpha(GOLD_IMAGE, 0, self.size)
        elif name == 'BREEZE':
            self.item = utils.Utils.load_image_alpha(BREEZE_IMAGE, 0, self.size)
        elif name == 'STENCH':
            self.item = utils.Utils.load_image_alpha(STENCH_IMAGE, 0, self.size)
        elif name == 'ARROW':
            self.item = utils.Utils.load_image_alpha(ARROW_IMAGE[0], 0, self.size)
        elif name == 'WALL':
            self.item = utils.Utils.load_image_alpha(WALL_IMAGE, 0, self.size)
        elif name == 'FLOOR':
            self.item = utils.Utils.load_image_alpha(CELL_IMAGE, 0, self.size)
        elif name == 'FLOOR HAVE GOLD':
            self.item = utils.Utils.load_image_alpha(CELL_GOLD_IMAGE, 0, self.size)

        self.rect = self.item.get_rect()
        self.rect.top = y - self.size // 2
        self.rect.left = x - self.size // 2

    def draw(self, screen: pygame):
        screen.blit(self.item, self.rect)

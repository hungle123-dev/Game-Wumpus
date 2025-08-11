import pygame

from constants import MARGIN, SPACING_CELL, CELL_SIZE
from utils import Utils


class Entity(object):
    def __init__(self, row, col, image, size: int = CELL_SIZE):
        self.row = row
        self.col = col
        self.image = Utils.load_image_alpha(image, 0, size)
        self.rect = self.image.get_rect()
        self.rect.top = row * CELL_SIZE + MARGIN["TOP"] + (row + 1) * SPACING_CELL
        self.rect.left = col * CELL_SIZE + MARGIN["LEFT"] + (col + 1) * SPACING_CELL

    def draw(self, screen: pygame):
        screen.blit(self.image, self.rect)

    def getRC(self):
        return [self.row, self.col]

    def change_image(self, image):
        self.image = Utils.load_image_alpha(image)

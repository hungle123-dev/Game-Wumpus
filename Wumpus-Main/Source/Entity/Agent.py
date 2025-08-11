import utils
from Entity.Entity import Entity
from Run.Action import Action
from constants import CELL_SIZE, MARGIN, SPACING_CELL, AGENT_IMAGE
from utils import Utils


class Agent(Entity):
    def __init__(self, row, col, N, size: int = CELL_SIZE):
        super().__init__(row, col, AGENT_IMAGE[0], size)
        self.N = N
        self.direction = 'RIGHT'
        self.has_gold = False

    def setRC(self, row, col):
        if not utils.Utils.isValid(row, col, self.N):
            return

        if row < self.row:
            self.image = Utils.load_image_alpha(AGENT_IMAGE[2])
        elif row > self.row:
            self.image = Utils.load_image_alpha(AGENT_IMAGE[3])

        if col < self.col:
            self.image = Utils.load_image_alpha(AGENT_IMAGE[1])
        elif col > self.col:
            self.image = Utils.load_image_alpha(AGENT_IMAGE[0])

        self.row = row
        self.col = col

        self.rect = self.image.get_rect()
        self.rect.top = row * CELL_SIZE + MARGIN["TOP"] + (row + 1) * SPACING_CELL
        self.rect.left = col * CELL_SIZE + MARGIN["LEFT"] + (col + 1) * SPACING_CELL

    def turn_to(self, direction):
        if direction == Action.TURN_RIGHT:
            self.change_image(AGENT_IMAGE[0])
            self.direction = 'RIGHT'
        elif direction == Action.TURN_LEFT:
            self.change_image(AGENT_IMAGE[1])
            self.direction = 'LEFT'
        elif direction == Action.TURN_UP:
            self.change_image(AGENT_IMAGE[2])
            self.direction = 'UP'
        elif direction == Action.TURN_DOWN:
            self.change_image(AGENT_IMAGE[3])
            self.direction = 'DOWN'

    def move_forward(self):
        if self.direction == 'RIGHT':
            self.setRC(self.row, self.col + 1)
        elif self.direction == 'LEFT':
            self.setRC(self.row, self.col - 1)
        elif self.direction == 'UP':
            self.setRC(self.row - 1, self.col)
        elif self.direction == 'DOWN':
            self.setRC(self.row + 1, self.col)

    def getNextPos(self):
        if self.direction == 'RIGHT':
            return [self.row, self.col + 1]
        elif self.direction == 'LEFT':
            return [self.row, self.col - 1]
        elif self.direction == 'UP':
            return [self.row - 1, self.col]
        elif self.direction == 'DOWN':
            return [self.row + 1, self.col]

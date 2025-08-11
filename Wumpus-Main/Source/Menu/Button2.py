import pygame

from Menu.Button import Button
from constants import BLACK, FONT_3, WHITE, RED


class Button2(Button):
    def __init__(self, x, y, width, height, screen, text_size=20, buttonText="Button", onClickFunction=None,
                 border_color=BLACK):
        super().__init__(x, y, width, height, screen, text_size, buttonText, onClickFunction, border_color)

        self.fillColors = {
            'normal': '#040D12',
            'hover': '#000000',
            'pressed': '#191717',
        }
        self.border_size = 6
        self.text_hover = RED

        self.font = pygame.font.Font(FONT_3, text_size)
        self.buttonSurf = self.font.render(buttonText, True, WHITE)

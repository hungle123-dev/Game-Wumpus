import pygame

from constants import FONT_2, BLACK, WHITE


class Button:
    def __init__(self, x, y, width, height, screen, text_size=20, buttonText="Button", onClickFunction=None,
                 border_color=BLACK):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onClickFunction = onClickFunction
        self.screen = screen
        self.border_color = border_color
        self.border_size = 4
        self.buttonText = buttonText
        self.text_hover = WHITE

        self.fillColors = {
            'normal': '#FF4500',
            'hover': '#FF6347',
            'pressed': '#FF7F50',
        }

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.font = pygame.font.Font(FONT_2, text_size)
        self.buttonSurf = self.font.render(self.buttonText, True, WHITE)

    def process(self):
        mousePos = pygame.mouse.get_pos()
        self.buttonSurface.fill(self.fillColors['normal'])
        self.buttonSurf = self.font.render(self.buttonText, True, WHITE)
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])
            self.buttonSurf = self.font.render(self.buttonText, True, self.text_hover)
            if pygame.mouse.get_pressed()[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                self.onClickFunction()

        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width / 2 - self.buttonSurf.get_rect().width / 2,
            self.buttonRect.height / 2 - self.buttonSurf.get_rect().height / 2
        ])
        pygame.draw.rect(self.buttonSurface, self.border_color, (0, 0, self.width, self.height), self.border_size)
        self.screen.blit(self.buttonSurface, self.buttonRect)

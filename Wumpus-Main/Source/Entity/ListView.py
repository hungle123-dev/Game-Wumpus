import pygame

from constants import GREY, WHITE, RED, WIDTH


class ListView:
    def __init__(self):
        self.font_size = 22
        self.font = pygame.font.Font(None, self.font_size)
        self.width = 200
        self.height = 300
        self.color = WHITE
        self.marginBottom = self.font_size//2+10
        self.padding = 0
        self.left = WIDTH - 200
        self.top = 100
        self.show_scroll = False

        self.scroll_position = 0
        self.scroll_speed = 5
        self.scrollbar_width = 14
        self.scrollbar_margin = 120
        self.scrollbar_rect = pygame.Rect(self.left+self.scrollbar_margin, self.top, self.scrollbar_width, self.height)

        # content of list view
        self.items = []

    def draw_list_view(self, screen: pygame):
        for i, item in enumerate(self.items):
            text = self.font.render(item, True, self.color)
            text_rect = text.get_rect()
            text_rect.topleft = (self.left-100, self.top + i * self.marginBottom - self.scroll_position)
            if text_rect.topleft[1] < self.top or text_rect.topleft[1] > self.top+self.height - self.font_size//2:
                continue
            screen.blit(text, text_rect)

    def draw_scrollbar(self, screen):
        pygame.draw.rect(screen, GREY, self.scrollbar_rect)

        handle_position = ((self.scroll_position / (len(self.items) * self.marginBottom - self.height)) *
                           (self.height - self.scrollbar_width)) + self.top
        handle_rect = pygame.Rect(self.left+self.scrollbar_margin, handle_position, self.scrollbar_width,
                                  self.scrollbar_width)
        pygame.draw.rect(screen, RED, handle_rect)

    def scroll_bottom(self):
        self.scroll_position = len(self.items) * self.marginBottom - self.height

    def scroll_up(self):
        self.scroll_position = max(0, self.scroll_position - self.scroll_speed)

    def scroll_down(self):
        self.scroll_position = min(len(self.items) * self.marginBottom - self.height, self.scroll_position
                                   + self.scroll_speed)

    def add_item(self, content):
        if content == "KILL_ALL_WUMPUS_AND_GRAB_ALL_FOOD":
            content = "DONE ALL ACTION"
        self.items.append(content.replace("_", " "))
        self.scroll_bottom()

    def show_scrollbar(self):
        self.show_scroll = True

    def hide_scrollbar(self):
        self.show_scroll = False

    def draw(self, screen):
        self.draw_list_view(screen)
        if self.show_scroll:
            self.draw_scrollbar(screen)

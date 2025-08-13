import pygame
from Menu.Button2 import Button2
from constants import WHITE

class Settings:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.visible = False
        self.wumpus_count = 2
        self.pit_probability = 0.2
        
        # Cooldown system
        self.last_button_press = 0
        self.cooldown_time = 500  # 500 milliseconds = 0.5 seconds
        
        # Create buttons for adjusting Wumpus count and Pit probability
        btn_width = 50
        btn_height = 50
        spacing = 20
        
        # Calculate x positions for the buttons (right side of screen)
        center_x = width - 250  # Center of settings panel
        minus_x = center_x - btn_width - spacing
        plus_x = center_x + spacing
        
        # Wumpus count controls
        base_y = (height - btn_height) // 2 - 60
        self.btn_wumpus_minus = Button2(
            minus_x, base_y,
            btn_width, btn_height,
            screen, 40, "-",
            self.decrease_wumpus,
            WHITE
        )
        
        self.btn_wumpus_plus = Button2(
            plus_x, base_y,
            btn_width, btn_height,
            screen, 40, "+",
            self.increase_wumpus,
            WHITE
        )
        
        # Pit probability controls
        base_y = (height - btn_height) // 2 + 60
        self.btn_pit_minus = Button2(
            minus_x, base_y,
            btn_width, btn_height,
            screen, 40, "-",
            self.decrease_pit_prob,
            WHITE
        )
        
        self.btn_pit_plus = Button2(
            plus_x, base_y,
            btn_width, btn_height,
            screen, 40, "+",
            self.increase_pit_prob,
            WHITE
        )

    def check_cooldown(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_button_press >= self.cooldown_time:
            self.last_button_press = current_time
            return True
        return False

    def increase_wumpus(self):
        if self.check_cooldown() and self.wumpus_count < 5:  # Maximum 5 Wumpus
            self.wumpus_count += 1

    def decrease_wumpus(self):
        if self.check_cooldown() and self.wumpus_count > 1:  # Minimum 1 Wumpus
            self.wumpus_count -= 1

    def increase_pit_prob(self):
        if self.check_cooldown() and self.pit_probability < 0.4:  # Maximum 40% probability
            self.pit_probability = round(self.pit_probability + 0.1, 1)

    def decrease_pit_prob(self):
        if self.check_cooldown() and self.pit_probability > 0.1:  # Minimum 10% probability
            self.pit_probability = round(self.pit_probability - 0.1, 1)

    def draw(self):
        if not self.visible:
            return

        # Draw semi-transparent background for settings panel
        settings_surface = pygame.Surface((400, 400))
        settings_surface.fill((0, 0, 0))
        settings_surface.set_alpha(200)
        settings_rect = settings_surface.get_rect(center=(self.width - 250, self.height // 2))
        self.screen.blit(settings_surface, settings_rect)

        # Draw settings title
        font = pygame.font.Font(None, 48)
        title = font.render("Game Settings", True, WHITE)
        title_rect = title.get_rect(center=(self.width - 250, (self.height - 100) // 2 - 150))
        self.screen.blit(title, title_rect)

        # Draw Wumpus count section
        wumpus_text = font.render(f"Wumpus Count: {self.wumpus_count}", True, WHITE)
        wumpus_rect = wumpus_text.get_rect(center=(self.width - 250, (self.height - 100) // 2 - 60))
        self.screen.blit(wumpus_text, wumpus_rect)
        
        # Draw Pit probability section
        pit_text = font.render(f"Pit Probability: {int(self.pit_probability * 100)}%", True, WHITE)
        pit_rect = pit_text.get_rect(center=(self.width - 250, (self.height - 100) // 2 + 60))
        self.screen.blit(pit_text, pit_rect)

        # Draw buttons
        self.btn_wumpus_minus.process()
        self.btn_wumpus_plus.process()
        self.btn_pit_minus.process()
        self.btn_pit_plus.process()

    def toggle(self):
        self.visible = not self.visible

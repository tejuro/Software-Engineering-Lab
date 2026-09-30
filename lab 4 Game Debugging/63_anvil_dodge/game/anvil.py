import random
import pygame

MIN_SPEED = 4.5
MAX_SPEED = 7.0


class Anvil:
    def __init__(self, screen_width):
        self.screen_width = screen_width
        self.width = 40
        self.height = 32
        self.x = random.randint(20, screen_width - self.width - 20)
        self.y = -self.height
        self.speed = random.uniform(MIN_SPEED, MAX_SPEED)

    def update(self):
        self.y += self.speed

    def is_off_screen(self, screen_height):
        return self.y > screen_height + 10

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def _blend(self, base, t):
        """Blend a grey base color toward orange-red by t (0 to 1)."""
        hot = (235, 70, 25)
        return tuple(int(b + (h - b) * t) for b, h in zip(base, hot))

    def _speed_ratio(self):
        t = (self.speed - MIN_SPEED) / (MAX_SPEED - MIN_SPEED)
        return max(0.0, min(1.0, t))

    def render(self, surface):
        # Task 3: fast anvils shift from grey to orange-red
        t = self._speed_ratio()
        top_color = self._blend((120, 120, 130), t)
        base_color = self._blend((80, 80, 90), t)
        outline_color = self._blend((200, 200, 210), t * 0.6)

        top_rect = pygame.Rect(int(self.x) + 4, int(self.y), self.width - 8, 14)
        pygame.draw.rect(surface, top_color, top_rect, border_radius=2)

        base_rect = pygame.Rect(int(self.x), int(self.y) + 14, self.width, 18)
        pygame.draw.rect(surface, base_color, base_rect, border_radius=3)
        pygame.draw.rect(surface, outline_color, base_rect, width=1, border_radius=3)
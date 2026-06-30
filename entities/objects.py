import pygame
from settings import *


class WorldObject:
    """Базовый класс для всего, что летит навстречу лисе по дороге"""
    def __init__(self, lane, obj_type, y_offset=0):
        self.lane = lane
        self.type = obj_type
        self.width = LANE_WIDTH - 25
        self.height = 40

        self.x = SIDE_WIDTH + (lane * LANE_WIDTH) + (LANE_WIDTH - self.width) // 2
        self.y = -100 - y_offset

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, speed):
        self.y += speed
        self.rect.y = self.y

    def draw(self, surface):
        if self.type == "log":
            pygame.draw.rect(surface, COLOR_LOG, self.rect, border_radius=5)
            pygame.draw.line(surface, (80, 40, 20), (self.rect.x + 5, self.y + 10),
                             (self.rect.x + self.width - 5, self.y + 10), 2)

        elif self.type == "rock":
            pygame.draw.ellipse(surface, COLOR_STONE, self.rect)

        elif self.type == "bush":
            pygame.draw.ellipse(surface, COLOR_BUSH, self.rect)
            pygame.draw.circle(surface, (200, 0, 0), (self.rect.centerx - 10, self.rect.centery), 3)
            pygame.draw.circle(surface, (200, 0, 0), (self.rect.centerx + 10, self.rect.centery + 5), 3)

        elif self.type == "firefly":
            pygame.draw.circle(surface, COLOR_FIREFLY, self.rect.center, 8)
            pygame.draw.circle(surface, (255, 255, 150), self.rect.center, 15, 1)
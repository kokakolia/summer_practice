import pygame
from settings import *


class Player:
    def __init__(self):
        self.lane = START_LANE
        self.energy = MAX_ENERGY
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE

        self.x = self._get_x_by_lane(self.lane)
        self.y = SCREEN_HEIGHT - self.height - 50

        self.target_x = self.x

    def _get_x_by_lane(self, lane):
        """Вычисляет центр полосы для игрока"""
        lane_center = SIDE_WIDTH + (lane * LANE_WIDTH) + (LANE_WIDTH // 2)
        return lane_center - self.width // 2

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            self.x = self._get_x_by_lane(self.lane)

    def move_right(self):
        if self.lane < LANE_COUNT - 1:
            self.lane += 1
            self.x = self._get_x_by_lane(self.lane)

    def update(self):
        if self.energy > 0:
            self.energy -= ENERGY_DRAIN_RATE
        else:
            self.energy = 0

    def draw(self, surface):
        points = [
            (self.x + self.width // 2, self.y),  # Нос
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(surface, COLOR_FOX, points)

        # Маленькие ушки
        pygame.draw.polygon(surface, COLOR_FOX,
                            [(self.x, self.y + 10), (self.x + 5, self.y - 5), (self.x + 10, self.y + 5)])
        pygame.draw.polygon(surface, COLOR_FOX,
                            [(self.x + self.width, self.y + 10), (self.x + self.width - 5, self.y - 5),
                             (self.x + self.width - 10, self.y + 5)])
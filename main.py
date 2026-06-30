import sys
import random
from settings import *
import pygame
from entities.player import Player
from entities.objects import WorldObject


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Midnight Fox")
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.game_state = "PLAYING"

        self.current_speed = INITIAL_SPEED
        self.score = 0

        self.player = Player()
        self.decorations = []
        self.world_objects = []

        self.obstacle_timer = pygame.time.get_ticks()
        self.firefly_timer = pygame.time.get_ticks()

        self.light_x = SCREEN_WIDTH // 2

        self._spawn_initial_decorations()
        self.vignette_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.current_vignette_radius = 500

        self.game_state = "MENU"
        self.menu_timer = 0

        button_w, button_h = 220, 50
        self.btn_restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_w - 10, 350, button_w, button_h)
        self.btn_menu_rect = pygame.Rect(SCREEN_WIDTH // 2 + 10, 350, button_w, button_h)
        self.btn_quit_menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 450, 200, 50)

    def _spawn_initial_decorations(self):
        for _ in range(25):
            self._spawn_decoration(random.randint(0, SCREEN_HEIGHT))

    def _spawn_decoration(self, y_pos=-100):
        side = random.choice(["left", "right"])
        for d in self.decorations:
            if d['side'] == side and abs(d['y'] - y_pos) < 120:
                return

        obj_type = random.choices(["tree", "stone", "stump"], weights=[70, 15, 15])[0]
        if side == "left":
            x = random.randint(10, SIDE_WIDTH - 80)
        else:
            x = random.randint(SCREEN_WIDTH - SIDE_WIDTH + 10, SCREEN_WIDTH - 80)

        self.decorations.append({'x': x, 'y': y_pos, 'type': obj_type, 'side': side})

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "MENU":
                        self.is_running = False
                    else:
                        self.reset_game()
                        self.game_state = "MENU"


            if self.game_state == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.game_state = "PLAYING"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.btn_quit_menu_rect.collidepoint(event.pos):
                            self.is_running = False

            elif self.game_state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_LEFT, pygame.K_a]: self.player.move_left()
                    if event.key in [pygame.K_RIGHT, pygame.K_d]: self.player.move_right()


            elif self.game_state == "GAMEOVER":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.btn_restart_rect.collidepoint(event.pos):
                            self.reset_game()
                        if self.btn_menu_rect.collidepoint(event.pos):
                            self.reset_game()
                            self.game_state = "MENU"

    def update(self):

        if self.game_state == "PLAYING":
            pygame.mouse.set_visible(False)
        else:
            pygame.mouse.set_visible(True)

        if self.game_state == "MENU":
            for deco in self.decorations:
                deco['y'] += self.current_speed * 0.5
            self.decorations = [d for d in self.decorations if d['y'] < SCREEN_HEIGHT + 100]
            if len(self.decorations) < 35: self._spawn_decoration()
            self.menu_timer += 1
            return

        if self.game_state == "GAMEOVER":
            if self.current_vignette_radius > 0:
                self.current_vignette_radius -= 4
                if self.current_vignette_radius < 0:
                    self.current_vignette_radius = 0
            return

        if self.player.energy <= 0:
            self.game_state = "GAMEOVER"
            return

        now = pygame.time.get_ticks()
        self.score += self.current_speed / 100
        if self.current_speed < MAX_SPEED:
            self.current_speed += SPEED_INCREMENT

        self.player.update()

        energy_ratio = self.player.energy / MAX_ENERGY
        current_spawn_rate = OBSTACLE_SPAWN_RATE
        if energy_ratio < 0.4:
            current_spawn_rate *= 1.15

        if now - self.obstacle_timer > current_spawn_rate:
            count = random.randint(2, 4)
            lanes = random.sample(range(LANE_COUNT), count)

            for l in lanes:
                too_close = any(o.lane == l and o.y < 150 for o in self.world_objects)

                if not too_close:
                    obj_t = random.choice(["log", "rock", "bush"])
                    y_dist = random.randint(0, 150)
                    self.world_objects.append(WorldObject(l, obj_t, y_offset=y_dist))

            self.obstacle_timer = now

        if now - self.firefly_timer > FIREFLY_SPAWN_RATE:
            occupied_lanes = [o.lane for o in self.world_objects if o.y < 200]
            available_lanes = [l for l in range(LANE_COUNT) if l not in occupied_lanes]

            if available_lanes:
                lane = random.choice(available_lanes)
                self.world_objects.append(WorldObject(lane, "firefly", y_offset=50))
            self.firefly_timer = now

        for deco in self.decorations:
            deco['y'] += self.current_speed
        self.decorations = [d for d in self.decorations if d['y'] < SCREEN_HEIGHT + 100]
        if len(self.decorations) < 35: self._spawn_decoration()

        for obj in self.world_objects[:]:
            obj.update(self.current_speed)
            player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)

            if obj.rect.colliderect(player_rect):
                if obj.type == "firefly":
                    self.player.energy = min(MAX_ENERGY, self.player.energy + ENERGY_RECOVERY)
                else:
                    self.player.energy = max(self.player.energy - ENERGY_PENALTY, 0)
                self.world_objects.remove(obj)
                continue

            if obj.y > SCREEN_HEIGHT + 50:
                self.world_objects.remove(obj)
        energy_ratio = self.player.energy / MAX_ENERGY
        target_radius = int(200 + energy_ratio * 250)
        self.current_vignette_radius += (target_radius - self.current_vignette_radius) * 0.1

    def _draw_tree(self, x, y):
        pygame.draw.rect(self.screen, COLOR_TREE_TRUNK, (x + 25, y + 60, 15, 30))
        for i in range(3):
            points = [(x + 32, y + i * 25), (x + 5, y + 50 + i * 15), (x + 60, y + 50 + i * 15)]
            pygame.draw.polygon(self.screen, COLOR_TREE_LEAVES, points)

    def _draw_stone(self, x, y):
        pygame.draw.ellipse(self.screen, COLOR_STONE, (x, y, 30, 20))
        pygame.draw.ellipse(self.screen, (60, 60, 65), (x + 5, y + 2, 15, 10))

    def _draw_stump(self, x, y):
        pygame.draw.rect(self.screen, COLOR_STUMP, (x, y, 25, 20))
        pygame.draw.ellipse(self.screen, (90, 70, 50), (x, y - 5, 25, 10))

    def draw_vignette(self):
        vignette_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        vignette_surf.fill((0, 0, 0))

        if self.game_state == "GAMEOVER":
            center_pos = (int(self.player.x + self.player.width // 2),
                          int(self.player.y + self.player.height // 2))
        else:
            energy_ratio = self.player.energy / MAX_ENERGY
            road_center = SCREEN_WIDTH // 2
            fox_center = self.player.x + self.player.width // 2

            if energy_ratio < 0.5:
                t = (0.5 - energy_ratio) * 2
                target_x = road_center + (fox_center - road_center) * t
            else:
                target_x = road_center

            self.light_x += (target_x - self.light_x) * 0.1
            center_pos = (int(self.light_x), int(self.player.y + self.player.height // 2))

        magic_color = (255, 0, 255)
        if self.current_vignette_radius > 0:
            pygame.draw.circle(vignette_surf, magic_color, center_pos, int(self.current_vignette_radius))
            if self.current_vignette_radius > 10:
                pygame.draw.circle(vignette_surf, (20, 20, 20), center_pos, int(self.current_vignette_radius + 40), 40)

        vignette_surf.set_colorkey(magic_color)
        vignette_surf.set_alpha(240)
        self.screen.blit(vignette_surf, (0, 0))

    def draw(self):
        self.screen.fill(COLOR_GRASS)
        pygame.draw.rect(self.screen, COLOR_PATH, (SIDE_WIDTH, 0, ROAD_WIDTH, SCREEN_HEIGHT))

        for i in range(1, LANE_COUNT):
            x = SIDE_WIDTH + i * LANE_WIDTH
            pygame.draw.line(self.screen, COLOR_LANE_SOFT, (x, 0), (x, SCREEN_HEIGHT), 1)

        for deco in sorted(self.decorations, key=lambda d: d['y']):
            if deco['type'] == "tree":
                self._draw_tree(deco['x'], deco['y'])
            elif deco['type'] == "stone":
                self._draw_stone(deco['x'], deco['y'])
            elif deco['type'] == "stump":
                self._draw_stump(deco['x'], deco['y'])

        for obj in self.world_objects:
            obj.draw(self.screen)

        self.player.draw(self.screen)

        if self.game_state == "MENU":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            f_title = pygame.font.SysFont("Arial", 64, bold=True)
            f_hint = pygame.font.SysFont("Arial", 24)

            title_text = f_title.render("MIDNIGHT FOX", True, (255, 140, 0))
            sub_title = f_hint.render("Путеводный свет", True, COLOR_WHITE)
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))
            self.screen.blit(sub_title, (SCREEN_WIDTH // 2 - sub_title.get_width() // 2, 230))

            if (self.menu_timer // 30) % 2 == 0:
                start_text = f_hint.render("НАЖМИТЕ ПРОБЕЛ ДЛЯ СТАРТА", True, (200, 200, 200))
                self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 400))

            mouse_pos = pygame.mouse.get_pos()
            color_quit = (120, 40, 40) if self.btn_quit_menu_rect.collidepoint(mouse_pos) else (80, 30, 30)
            pygame.draw.rect(self.screen, color_quit, self.btn_quit_menu_rect, border_radius=10)

            exit_txt = f_hint.render("ВЫХОД", True, COLOR_WHITE)
            self.screen.blit(exit_txt, (self.btn_quit_menu_rect.centerx - exit_txt.get_width() // 2,
                                        self.btn_quit_menu_rect.centery - exit_txt.get_height() // 2))

        if self.game_state == "PLAYING" or self.game_state == "GAMEOVER":
            self.draw_vignette()
            font = pygame.font.SysFont("Arial", 20, bold=True)
            self.screen.blit(font.render(f"Distance: {int(self.score)}m", True, COLOR_WHITE), (20, 20))
            e_color = (255, 255, 0) if self.player.energy > 30 else (255, 50, 50)
            self.screen.blit(font.render(f"Energy: {int(self.player.energy)}%", True, e_color), (20, 50))

            if self.game_state == "GAMEOVER" and self.current_vignette_radius < 10:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                self.screen.blit(overlay, (0, 0))

                f_big = pygame.font.SysFont("Arial", 48, bold=True)
                f_sm = pygame.font.SysFont("Arial", 24, bold=True)

                m1 = f_big.render("ТЬМА ПОГЛОТИЛА ВАС", True, (255, 50, 50))
                m2 = f_sm.render(f"Ваш результат: {int(self.score)}м", True, COLOR_WHITE)
                self.screen.blit(m1, (SCREEN_WIDTH // 2 - m1.get_width() // 2, 180))
                self.screen.blit(m2, (SCREEN_WIDTH // 2 - m2.get_width() // 2, 260))

                mouse_pos = pygame.mouse.get_pos()

                color_restart = (100, 100, 100) if self.btn_restart_rect.collidepoint(mouse_pos) else (60, 60, 60)
                pygame.draw.rect(self.screen, color_restart, self.btn_restart_rect, border_radius=10)
                txt_restart = f_sm.render("НОВАЯ ИГРА", True, COLOR_WHITE)
                self.screen.blit(txt_restart, (self.btn_restart_rect.centerx - txt_restart.get_width() // 2,
                                               self.btn_restart_rect.centery - txt_restart.get_height() // 2))

                color_menu = (100, 100, 100) if self.btn_menu_rect.collidepoint(mouse_pos) else (60, 60, 60)
                pygame.draw.rect(self.screen, color_menu, self.btn_menu_rect, border_radius=10)
                txt_menu = f_sm.render("В МЕНЮ", True, COLOR_WHITE)
                self.screen.blit(txt_menu, (self.btn_menu_rect.centerx - txt_menu.get_width() // 2,
                                            self.btn_menu_rect.centery - txt_menu.get_height() // 2))

        pygame.display.flip()

    def reset_game(self):
        self.player = Player()
        self.world_objects = []
        self.decorations = []
        self._spawn_initial_decorations()
        self.score = 0
        self.current_speed = INITIAL_SPEED
        self.game_state = "PLAYING"
        self.obstacle_timer = pygame.time.get_ticks()
        self.current_vignette_radius = 500
        self.light_x = SCREEN_WIDTH // 2

    def run(self):
        while self.is_running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
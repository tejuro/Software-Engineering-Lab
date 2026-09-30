import random
import pygame
from game.player import Player
from game.anvil import Anvil

BASE_SPAWN_DELAY = 700    # ms
MIN_SPAWN_DELAY = 200     # ms
DELAY_DECAY_PER_SEC = 40  # ms removed per second survived (40 makes the ramp visible in a short video)


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ground_y = height - 20
        self.player = Player(width, height)
        self.anvils = []

        # Task 4: impact effects
        self.particles = []
        self.shake_frames = 0

        self.spawn_delay = BASE_SPAWN_DELAY
        self.last_spawn_time = pygame.time.get_ticks()

        self.start_ticks = pygame.time.get_ticks()
        self.survival_time = 0
        self.game_state = "PLAYING"

        self.font_big = pygame.font.SysFont(None, 52)
        self.font_medium = pygame.font.SysFont(None, 34)
        self.font_small = pygame.font.SysFont(None, 24)

    def handle_event(self, event):
        if self.game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()

    # ---------- Task 4 helpers ----------
    def _ground_impact(self, anvil):
        cx = anvil.rect.centerx
        for _ in range(20):
            self.particles.append({
                "x": cx + random.uniform(-15, 15),
                "y": self.ground_y,
                "vx": random.uniform(-2.5, 2.5),
                "vy": random.uniform(-4.5, -1),
                "life": random.randint(15, 30),  # frames
                "max_life": 30,
                "size": random.randint(3, 6),
            })
        self.shake_frames = 10

    def _update_particles(self):
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.25  # gravity
            p["life"] -= 1
        self.particles = [p for p in self.particles if p["life"] > 0]
        if self.shake_frames > 0:
            self.shake_frames -= 1

    # ---------- update ----------
    def update(self):
        self._update_particles()  # dust keeps animating even after game over

        if self.game_state != "PLAYING":
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()

        self.player.update()

        self.survival_time = (pygame.time.get_ticks() - self.start_ticks) // 1000

        # Task 2: spawn delay shrinks the longer you survive, down to a floor
        self.spawn_delay = max(
            MIN_SPAWN_DELAY,
            BASE_SPAWN_DELAY - self.survival_time * DELAY_DECAY_PER_SEC,
        )

        now = pygame.time.get_ticks()
        if now - self.last_spawn_time >= self.spawn_delay:
            self.anvils.append(Anvil(self.width))
            self.last_spawn_time = now

        player_rect = self.player.rect
        for anvil in self.anvils[:]:
            anvil.update()

            if player_rect.colliderect(anvil.rect):
                self.game_state = "GAME_OVER"
                break

            # Task 4: anvil strikes the ground -> effect, then remove
            if anvil.rect.bottom >= self.ground_y:
                self._ground_impact(anvil)
                self.anvils.remove(anvil)
            elif anvil.is_off_screen(self.height):
                self.anvils.remove(anvil)

    def reset(self):
        self.player = Player(self.width, self.height)
        self.anvils.clear()
        self.particles.clear()
        self.shake_frames = 0
        self.spawn_delay = BASE_SPAWN_DELAY
        self.start_ticks = pygame.time.get_ticks()
        self.last_spawn_time = pygame.time.get_ticks()
        self.survival_time = 0
        self.game_state = "PLAYING"

    # ---------- render ----------
    def render(self, screen):
        # draw the world onto a scene surface so it can be shaken
        scene = pygame.Surface((self.width, self.height))
        scene.fill((35, 38, 45))

        pygame.draw.rect(scene, (70, 75, 85), (0, self.ground_y, self.width, 20))
        pygame.draw.line(scene, (160, 90, 40), (0, self.ground_y), (self.width, self.ground_y), 3)

        self.player.render(scene)
        for anvil in self.anvils:
            anvil.render(scene)

        # brighter dust so it shows up on screen recordings
        for p in self.particles:
            shade = int(180 * p["life"] / p["max_life"]) + 40
            pygame.draw.circle(scene, (min(255, shade + 40), min(255, shade + 20), shade),
                               (int(p["x"]), int(p["y"])), p["size"])

        ox = oy = 0
        if self.shake_frames > 0:
            ox = random.randint(-5, 5)
            oy = random.randint(-5, 5)
        screen.fill((0, 0, 0))
        screen.blit(scene, (ox, oy))

        # HUD and overlay are drawn on the screen directly, so they don't shake
        time_surf = self.font_medium.render(f"Survival Time: {self.survival_time}s", True, (240, 240, 240))
        screen.blit(time_surf, (20, 20))

        inst_surf = self.font_small.render("Use [A/D] or [Arrow Keys] to Dodge", True, (170, 175, 185))
        screen.blit(inst_surf, (self.width - inst_surf.get_width() - 20, 25))

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            screen.blit(overlay, (0, 0))

            over_surf = self.font_big.render("CRUSHED! GAME OVER", True, (235, 65, 65))
            screen.blit(over_surf, (self.width // 2 - over_surf.get_width() // 2, self.height // 2 - 60))

            score_surf = self.font_medium.render(f"You survived: {self.survival_time} seconds", True, (255, 255, 255))
            screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, self.height // 2))

            restart_surf = self.font_small.render("Press [R] to Play Again", True, (200, 200, 200))
            screen.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 50))
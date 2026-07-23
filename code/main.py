import pygame
from sys import exit
from os.path import join
from math import sin
from random import randint, uniform
from pygame.math import Vector2
from assets import load

INTERAL_W, INTERAL_H = 1280, 720
SCALE = 1

BG_COLOR = "#251137"
TEXT_COLOR = (240, 240, 240)
ACCENT_COLOR = (122, 236, 255)


def lerp(a, b, t):
    return a + (b - a) * t


def ease_out(t):
    """Fast at the start, gentle at the end."""
    return 1 - (1 - t) ** 3


class Player(pygame.sprite.Sprite):
    def __init__(self, groups, assets, laser_sprites, all_sprites):
        super().__init__(groups)
        self.all_sprites = all_sprites
        self.laser_sprites = laser_sprites
        self.laser_sound = assets.laser_sound
        self.laser_surf = assets.laser
        self.original_surf = assets.player
        self.image = self.original_surf
        self.rect = self.image.get_frect(center=(INTERAL_W / 2, INTERAL_H / 2))
        self.player_direction = Vector2()
        self.player_speed = 300

        # cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

    def laser_timer(self):
        if not self.can_shoot:
            if pygame.time.get_ticks() >= self.laser_shoot_time + self.cooldown_duration:
                self.can_shoot = True

    def player_input(self):
        keys = pygame.key.get_pressed()
        self.player_direction.x = int(keys[pygame.K_RIGHT] - int(keys[pygame.K_LEFT]))
        self.player_direction.y = int(keys[pygame.K_DOWN] - int(keys[pygame.K_UP]))
        self.player_direction = self.player_direction.normalize() if self.player_direction else self.player_direction

        recent_keys = pygame.key.get_just_pressed()

        # laser shot
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(self.laser_surf, self.rect.midtop, (self.all_sprites, self.laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            self.laser_sound.play()

    def movement(self, dt):
        self.rect.center += self.player_direction * self.player_speed * dt
        # --- Boundaries ---
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= INTERAL_W:
            self.rect.right = INTERAL_W
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= INTERAL_H:
            self.rect.bottom = INTERAL_H

    def update(self, dt):
        self.player_input()
        self.movement(dt)
        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=(randint(0, INTERAL_W), randint(0, INTERAL_H)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=pos)

    def kill_laser(self):
        if self.rect.bottom < 0:
            self.kill()

    def movement(self, dt):
        self.rect.centery -= 650 * dt

    def update(self, dt):
        self.movement(dt)
        self.kill_laser()

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, groups, pos, surf):
        super().__init__(groups)
        self.original_surf = surf
        self.image = self.original_surf
        self.rect = self.image.get_frect(center=pos)
        self.time_created = pygame.time.get_ticks()
        self.life_time = 7500
        self.direction = Vector2(uniform(-.5, .5),1)
        self.speed = randint(350, 500)

        # Rotation
        self.rotation = 0
        self.rotation_speed = randint(50, 80)

    def rotate_asteroid(self, dt):
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center=(self.rect.center))

    def movement(self, dt):
        self.rect.center += self.direction * self.speed * dt
        self.rotation += 50 * dt

    def kill_asteroid(self):
        if pygame.time.get_ticks() >= self.time_created + self.life_time:
            self.kill()

    def update(self, dt):
        self.movement(dt)
        self.rotate_asteroid(dt)
        self.kill_asteroid()

class AnimatedExposion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.animation_frames = frames
        self.animation_index = 0
        self.animation_active = True
        self.image = self.animation_frames[self.animation_index]
        self.rect = self.image.get_frect(center=pos)

    def animation(self, dt):
        self.animation_index += 75 * dt
        if self.animation_index >= len(self.animation_frames):
            self.animation_active = False
        self.image = self.animation_frames[int(self.animation_index) % len(self.animation_frames)]

    def kill_animation(self):
        if not self.animation_active:
            self.kill()

    def update(self, dt):
        self.animation(dt)
        self.kill_animation()


class Button:
    """A menu button that grows on hover and wipes its fill in from the left."""

    def __init__(self, label, center, font, size=(320, 66)):
        self.label = label
        self.font = font
        self.base_rect = pygame.Rect(0, 0, *size)
        self.base_rect.center = center
        self.hover = 0.0    # eased 0 -> 1, how hovered the button is
        self.press = 0.0    # eased 1 -> 0, fades out after a click

    @property
    def rect(self):
        grow = int(14 * self.hover) - int(10 * self.press)
        return self.base_rect.inflate(grow, grow // 2)

    def update(self, dt, mouse_pos):
        target = 1.0 if self.base_rect.collidepoint(mouse_pos) else 0.0
        self.hover += (target - self.hover) * min(1.0, 14 * dt)
        self.press = max(0.0, self.press - 5 * dt)

    def clicked(self, mouse_pos):
        if self.base_rect.collidepoint(mouse_pos):
            self.press = 1.0
            return True
        return False

    def draw(self, surface):
        rect = self.rect
        text_rect = self.font.size(self.label)
        text_pos = (rect.centerx - text_rect[0] / 2, rect.centery - text_rect[1] / 2)

        # unfilled state: outline plus accent text
        pygame.draw.rect(surface, ACCENT_COLOR, rect, 3, border_radius=12)
        surface.blit(self.font.render(self.label, True, ACCENT_COLOR), text_pos)

        # filled state, revealed left to right by the hover amount
        if self.hover > 0.01:
            wipe = rect.copy()
            wipe.width = int(rect.width * self.hover)
            surface.set_clip(wipe)
            pygame.draw.rect(surface, ACCENT_COLOR, rect, 0, border_radius=12)
            surface.blit(self.font.render(self.label, True, BG_COLOR), text_pos)
            surface.set_clip(None)


class Transition:
    """Two bars that close over the screen, swap the scene, then open again."""

    DURATION = 0.35

    def __init__(self):
        self.active = False
        self.closing = True
        self.t = 0.0
        self.callback = None

    def start(self, callback):
        if self.active:
            return
        self.active = True
        self.closing = True
        self.t = 0.0
        self.callback = callback

    def update(self, dt):
        if not self.active:
            return
        self.t += dt / self.DURATION
        if self.t >= 1.0:
            self.t = 0.0
            if self.closing:
                self.closing = False
                if self.callback:
                    self.callback()
                    self.callback = None
            else:
                self.active = False

    def draw(self, surface):
        if not self.active:
            return
        amount = ease_out(self.t) if self.closing else 1 - ease_out(self.t)
        height = (INTERAL_H / 2) * amount
        pygame.draw.rect(surface, (10, 5, 18), (0, 0, INTERAL_W, height))
        pygame.draw.rect(surface, (10, 5, 18), (0, INTERAL_H - height, INTERAL_W, height))


def draw_score(surface, assets, score):
    text_surf = assets.font.render(f"{score}", True, TEXT_COLOR)
    text_rect = text_surf.get_frect(midbottom=(INTERAL_W / 2, INTERAL_H - 30))
    surface.blit(text_surf, text_rect)
    pygame.draw.rect(surface, TEXT_COLOR, text_rect.inflate(20, 16).move(0, -5), 5, 2)


def draw_centered(surface, font, text, color, y):
    surf = font.render(text, True, color)
    surface.blit(surf, surf.get_frect(center=(INTERAL_W / 2, y)))


class Game():
    def __init__(self):
        pygame.display.set_caption("Space Shooter")
        self.surface = pygame.Surface((INTERAL_W, INTERAL_H))
        self.screen = pygame.display.set_mode((INTERAL_W * SCALE, INTERAL_H * SCALE))
        self.clock = pygame.time.Clock()
        self.assets = load()

        # --- Sprite groups ---
        self.stars = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.asteroid_sprites = pygame.sprite.Group()
        self.laser_sprites = pygame.sprite.Group()

        for _ in range(50):
            Star(self.stars, self.assets.star)

        self.asteroid_event = pygame.event.custom_type()
        pygame.time.set_timer(self.asteroid_event, 500)

        # --- Menu / state ---
        self.state = "menu"     # menu | playing | dying | gameover
        self.transition = Transition()
        self.player = None
        self.score = 0
        self.best_score = 0
        self.round_start = 0
        self.death_time = 0
        self.elapsed = 0.0      # drives the title bob

        self.menu_buttons = [
            Button("Play", (INTERAL_W / 2, 420), self.assets.menu_font),
            Button("Quit", (INTERAL_W / 2, 505), self.assets.menu_font),
        ]
        self.gameover_buttons = [
            Button("Play Again", (INTERAL_W / 2, 440), self.assets.menu_font),
            Button("Quit", (INTERAL_W / 2, 525), self.assets.menu_font),
        ]

    # --- State changes ---

    def start_round(self):
        self.all_sprites.empty()
        self.asteroid_sprites.empty()
        self.laser_sprites.empty()
        self.player = Player(self.all_sprites, self.assets, self.laser_sprites, self.all_sprites)
        self.score = 0
        self.round_start = pygame.time.get_ticks()
        self.state = "playing"

    def kill_player(self):
        AnimatedExposion(self.assets.explosion, self.player.rect.center, self.all_sprites)
        self.assets.damage_sound.play()
        self.player.kill()
        self.player = None
        self.best_score = max(self.best_score, self.score)
        self.death_time = pygame.time.get_ticks()
        self.state = "dying"

    def show_gameover(self):
        self.state = "gameover"

    def quit(self):
        pygame.quit()
        exit()

    # --- Update ---

    def collisions(self):
        if self.player and pygame.sprite.spritecollide(self.player, self.asteroid_sprites, True, pygame.sprite.collide_mask):
            self.kill_player()

        for laser in self.laser_sprites:
            if pygame.sprite.spritecollide(laser, self.asteroid_sprites, True):
                laser.kill()
                AnimatedExposion(self.assets.explosion, laser.rect.midtop, self.all_sprites)
                self.assets.explosion_sound.play()

    def active_buttons(self):
        if self.state == "menu":
            return self.menu_buttons
        if self.state == "gameover":
            return self.gameover_buttons
        return []

    def on_click(self, mouse_pos):
        if self.transition.active:
            return
        for button in self.active_buttons():
            if button.clicked(mouse_pos):
                if button.label == "Quit":
                    self.quit()
                else:
                    self.transition.start(self.start_round)

    # --- Render ---

    def draw_menu(self):
        bob = sin(self.elapsed * 2) * 8
        draw_centered(self.surface, self.assets.title_font, "SPACE SHOOTER", ACCENT_COLOR, 240 + bob)
        draw_centered(self.surface, self.assets.font, "Arrows to fly, Space to shoot", TEXT_COLOR, 320 + bob)
        if self.best_score:
            draw_centered(self.surface, self.assets.font, f"Best: {self.best_score}", TEXT_COLOR, 610)

    def draw_gameover(self):
        draw_centered(self.surface, self.assets.title_font, "YOU DIED", (255, 120, 120), 250)
        draw_centered(self.surface, self.assets.font, f"Score: {self.score}", TEXT_COLOR, 330)
        draw_centered(self.surface, self.assets.font, f"Best: {self.best_score}", TEXT_COLOR, 370)

    def run(self):
        self.assets.main_music.play(-1)
        while True:
            dt = self.clock.tick_busy_loop(100) / 1000
            self.elapsed += dt
            mouse_pos = [pos / SCALE for pos in pygame.mouse.get_pos()]

            # --- Input ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.on_click(mouse_pos)
                if event.type == self.asteroid_event and self.state == "playing":
                    x, y = randint(0, INTERAL_W), randint(-200, -100)
                    Asteroid((self.all_sprites, self.asteroid_sprites), (x, y), self.assets.asteroid)

            # --- Update ---
            self.transition.update(dt)
            self.all_sprites.update(dt)
            self.collisions()

            if self.state == "playing":
                self.score = (pygame.time.get_ticks() - self.round_start) // 100
            elif self.state == "dying" and pygame.time.get_ticks() >= self.death_time + 900:
                self.transition.start(self.show_gameover)

            for button in self.active_buttons():
                button.update(dt, mouse_pos)

            # --- Render ---
            self.surface.fill(BG_COLOR)
            self.stars.draw(self.surface)
            self.all_sprites.draw(self.surface)

            if self.state in ("playing", "dying"):
                draw_score(self.surface, self.assets, self.score)
            elif self.state == "menu":
                self.draw_menu()
            elif self.state == "gameover":
                self.draw_gameover()

            for button in self.active_buttons():
                button.draw(self.surface)

            self.transition.draw(self.surface)

            # --- Scale ---
            scaled = pygame.transform.smoothscale(self.surface,(INTERAL_W * SCALE, INTERAL_H * SCALE))
            self.screen.blit(scaled, (0, 0))
            pygame.display.flip()


Game().run()

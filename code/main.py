import pygame
from sys import exit
from os.path import join
from random import randint, uniform
from pygame.math import Vector2
from assets import load

INTERAL_W, INTERAL_H = 1280, 720
SCALE = 1


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

def display_score(surface, assets):
    current_time = pygame.time.get_ticks() // 100
    text_surf = assets.font.render(f"{current_time}", True, (240, 240, 240))
    text_rect = text_surf.get_frect(midbottom=(INTERAL_W / 2, INTERAL_H - 30))
    surface.blit(text_surf, text_rect)
    pygame.draw.rect(surface, (240, 240, 240), text_rect.inflate(20, 16).move(0, -5), 5, 2)



class Game():
    def __init__(self):
        pygame.display.set_caption("Space Shooter")
        self.surface = pygame.Surface((INTERAL_W, INTERAL_H))
        self.screen = pygame.display.set_mode((INTERAL_W * SCALE, INTERAL_H * SCALE))
        self.clock = pygame.time.Clock()
        self.assets = load()

        # --- Sprite groups ---
        self.all_sprites = pygame.sprite.Group()
        self.asteroid_sprites = pygame.sprite.Group()
        self.laser_sprites = pygame.sprite.Group()

        for _ in range(50):
            Star(self.all_sprites, self.assets.star)
        self.player = Player(self.all_sprites, self.assets, self.laser_sprites, self.all_sprites)
        
        self.asteroid_event = pygame.event.custom_type()
        pygame.time.set_timer(self.asteroid_event, 500)


    def collisions(self):
        collision_sprites = pygame.sprite.spritecollide(self.player, self.asteroid_sprites, True, pygame.sprite.collide_mask)
        if collision_sprites:
            print("died")
            self.assets.damage_sound.play()

        for laser in self.laser_sprites:
            if pygame.sprite.spritecollide(laser, self.asteroid_sprites, True):
                laser.kill()
                AnimatedExposion(self.assets.explosion, laser.rect.midtop, self.all_sprites)
                self.assets.explosion_sound.play()

    def run(self):
        self.assets.main_music.play(-1)
        while True:
            dt = self.clock.tick_busy_loop(100) / 1000

            # --- Input ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == self.asteroid_event:
                    x, y = randint(0, INTERAL_W), randint(-200, -100)
                    Asteroid((self.all_sprites, self.asteroid_sprites), (x, y), self.assets.asteroid)

            # --- Update ---
            self.all_sprites.update(dt)
            self.collisions()

            # --- Render ---
            self.surface.fill("#251137")
            self.all_sprites.draw(self.surface)
            display_score(self.surface, self.assets)

            # --- Scale ---
            scaled = pygame.transform.smoothscale(self.surface,(INTERAL_W * SCALE, INTERAL_H * SCALE))
            self.screen.blit(scaled, (0, 0))
            pygame.display.flip()


Game().run()
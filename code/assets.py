import pygame
from os.path import join
from dataclasses import dataclass

pygame.init()

@dataclass
class Assets:
    player : pygame.Surface
    star : pygame.Surface
    laser : pygame.Surface
    asteroid : pygame.Surface
    explosion : list[pygame.Surface]
    font : pygame.font.Font
    menu_font : pygame.font.Font
    title_font : pygame.font.Font
    explosion_sound : pygame.mixer.Sound
    damage_sound : pygame.mixer.Sound
    laser_sound : pygame.mixer.Sound
    main_music : pygame.mixer.Sound

def load():
    explosion_sound = pygame.mixer.Sound(join("audio", "explosion_sound.wav"))
    explosion_sound.set_volume(.2)
    laser_sound = pygame.mixer.Sound(join("audio", "laser_sound.wav"))
    laser_sound.set_volume(.2)
    damage_sound = pygame.mixer.Sound(join("audio", "damage_sound.ogg"))
    damage_sound.set_volume(.2)
    main_music = pygame.mixer.Sound(join("audio", "main_music.wav"))
    main_music.set_volume(.2)

    return Assets(
        player=pygame.image.load(join("images", "player.png")).convert_alpha(),
        star=pygame.transform.smoothscale_by((pygame.image.load(join("images", "star.png")).convert_alpha()), .5), 
        laser=pygame.image.load(join("images", "laser.png")).convert_alpha(), 
        asteroid=pygame.image.load(join("images", "asteroid.png")).convert_alpha(),
        explosion=[pygame.image.load(join("images", "explosion", f"{i}.png" )).convert_alpha() for i in range (21)],
        font=pygame.font.Font(join("images", "Oxanium-Bold.ttf"), 32),
        menu_font=pygame.font.Font(join("images", "Oxanium-Bold.ttf"), 34),
        title_font=pygame.font.Font(join("images", "Oxanium-Bold.ttf"), 82),
        explosion_sound=explosion_sound, 
        damage_sound=damage_sound,
        laser_sound=laser_sound,
        main_music=main_music
        )

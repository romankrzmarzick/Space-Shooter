# Space Shooter

A top-down arcade shooter in Python and pygame. You fly a ship, shoot lasers, and dodge
asteroids. Your score is how long you survive.

Has sound effects, background music, and a frame-by-frame explosion animation when
something gets hit.

## Running it

You need Python and pygame:

```
pip install pygame
```

Then run it from the project folder:

```
python code/main.py
```

## Controls

| Key | Does |
| --- | --- |
| Arrow keys | Fly |
| Space | Shoot |

Your laser has a short cooldown, so holding Space won't spam shots.

## How it's put together

- `code/main.py` — the ship, lasers, asteroids, collisions, and the game loop
- `code/assets.py` — loads every image and sound once at startup
- `images/` — sprites, explosion frames, and the font
- `audio/` — music and sound effects

Loading the assets in one place keeps the game loop from touching the disk while it runs.

# Space Shooter

A top-down arcade shooter in Python and pygame. Fly a ship, shoot lasers, dodge asteroids.
Your score is how long you survive — one hit and you're gone.

Has sound effects, background music, a frame-by-frame explosion animation, and a menu with
animated buttons.

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
| Mouse | Menu buttons |

Your laser has a short cooldown, so holding Space won't spam shots.

## Playing

Click **Play** to start. An asteroid that touches your ship destroys it — the ship blows
up, the run ends, and the game-over screen shows your score and your best so far. Click
**Play Again** for a fresh run.

## How it's put together

- `code/main.py` — the ship, lasers, asteroids, collisions, menus, and the game loop
- `code/assets.py` — loads every image, font, and sound once at startup
- `images/` — sprites, explosion frames, and the font
- `audio/` — music and sound effects

Loading the assets in one place keeps the game loop from touching the disk while it runs.

The game is a small state machine — `menu`, `playing`, `dying`, `gameover` — and every
switch between states goes through a wipe transition, so the scene only changes while the
screen is covered.

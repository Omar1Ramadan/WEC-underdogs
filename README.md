# Modern Asteroid Blitz

**Modern Asteroid Blitz** is a fast-paced 2D space shooter built with Python and Pygame. Players control a spaceship to destroy asteroids, enemies, and bosses while collecting power-ups and progressing through increasingly challenging levels.

---

## Features

### Gameplay
- **Player Movement**: Smooth, friction-based controls for enhanced maneuverability.
- **Shooting Mechanics**: 
  - Normal projectiles and powerful special projectiles (consuming special ammo).
- **Power-Ups**: Collectable items that replenish ammo, shields, or grant special ammo.
- **Enemy Variety**:
  - Basic enemies with simple AI.
  - Progressive difficulty scaling with faster and tougher enemies.
  - Multi-shot and boss enemies as the game progresses.

### Visuals & Effects
- **Dynamic Background**: A scrolling starfield to simulate depth in space.
- **Particles**: Explosions, engine thrusters, and projectile trails for a polished look.
- **Custom Sprites**: High-quality enemy and player ship sprites with pixel-perfect collision detection.

### Audio
- Add engaging sound effects for projectiles, explosions, and collisions (optional to implement).

---

## Controls

| Key        | Action                                |
|------------|---------------------------------------|
| `Arrow Keys` / `WASD` | Move the spaceship                |
| `Space`    | Fire normal projectiles               |
| `Q`        | Fire a burst of special projectiles (if ammo is available) |
| `R`        | Restart the game after Game Over      |
| `P`        | Pause the game                        |

---

## Objectives
- **Survive**: Avoid collisions with asteroids, enemies, and their projectiles.
- **Destroy**: Destroy asteroids and enemies to gain points.
- **Level Up**: Progress to higher levels with harder challenges.
- **Collect Power-Ups**: Restore shields, ammo, and special weapons.

---

## Power-Ups

- **Ammo Power-Up**: Replenishes 20 normal ammo.
- **Shield Power-Up**: Restores 50 shield points.
- **Special Ammo Power-Up**: Grants 3 special ammo.

---

## How to Run the Game

1. **Install Pygame**:
   ```bash
   pip install pygame

import pygame
import random
import math
from pygame import mixer
import os

# Initialize Pygame and mixer
pygame.init()
mixer.init()

# Set up the display with a larger resolution
WIDTH = 1280
HEIGHT = 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Modern Asteroid Blitz")

# Colors with modern palette
SPACE_BLUE = (13, 20, 36)
NEON_BLUE = (0, 219, 255)
NEON_PINK = (255, 16, 240)
NEON_GREEN = (57, 255, 20)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Load and scale assets (using colored shapes as placeholders)
def create_player_ship():
    surface = pygame.Surface((40, 50), pygame.SRCALPHA)
    # Create a more detailed ship shape
    points = [(20, 0), (40, 45), (30, 35), (20, 45), (10, 35), (0, 45)]
    pygame.draw.polygon(surface, NEON_BLUE, points)
    # Add engine glow
    pygame.draw.polygon(surface, NEON_PINK, [(15, 45), (25, 45), (20, 50)])
    return surface

def create_shield_effect():
    surface = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.circle(surface, (*NEON_BLUE, 128), (30, 30), 29, 2)
    return surface

class ParticleEffect:
    def __init__(self, x, y, color):
        self.particles = []
        self.x = x
        self.y = y
        self.color = color
        
    def create_particles(self, amount):
        for _ in range(amount):
            particle = {
                'x': self.x,
                'y': self.y,
                'velocity_x': random.uniform(-2, 2),
                'velocity_y': random.uniform(-2, 2),
                'lifetime': random.randint(20, 40),
                'size': random.randint(2, 4)
            }
            self.particles.append(particle)
            
    def update(self):
        surviving_particles = []
        for particle in self.particles:
            particle['x'] += particle['velocity_x']
            particle['y'] += particle['velocity_y']
            particle['lifetime'] -= 1
            if particle['lifetime'] > 0:
                surviving_particles.append(particle)
        self.particles = surviving_particles
        
    def draw(self, surface):
        for particle in self.particles:
            alpha = min(255, particle['lifetime'] * 6)
            particle_surface = pygame.Surface((particle['size'], particle['size']))
            particle_surface.fill(self.color)
            particle_surface.set_alpha(alpha)
            surface.blit(particle_surface, (particle['x'], particle['y']))

class ModernPlayer(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = create_player_ship()
        self.image = self.original_image
        self.shield_image = create_shield_effect()
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 100
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = 0.5
        self.max_speed = 8
        self.friction = 0.98
        self.angle = 0
        self.health = 100
        self.shield = 100
        self.ammunition = 50
        self.special_ammo = 5
        self.invincibility_timer = 0
        self.engine_particles = ParticleEffect(self.rect.centerx, self.rect.bottom, NEON_PINK)

    def update(self):
        # Enhanced movement with acceleration
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity.x = max(self.velocity.x - self.acceleration, -self.max_speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity.x = min(self.velocity.x + self.acceleration, self.max_speed)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.velocity.y = max(self.velocity.y - self.acceleration, -self.max_speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velocity.y = min(self.velocity.y + self.acceleration, self.max_speed)

        # Apply velocity and friction
        self.velocity *= self.friction
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Screen boundaries with bounce effect
        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity.x *= -0.5
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.velocity.x *= -0.5
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity.y *= -0.5
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity.y *= -0.5

        # Rotation based on movement direction
        if abs(self.velocity.x) > 0.1 or abs(self.velocity.y) > 0.1:
            self.angle = math.degrees(math.atan2(-self.velocity.x, -self.velocity.y))
        
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # Update engine particles
        if abs(self.velocity.x) > 0.5 or abs(self.velocity.y) > 0.5:
            self.engine_particles.x = self.rect.centerx
            self.engine_particles.y = self.rect.bottom
            self.engine_particles.create_particles(1)
        self.engine_particles.update()

        # Update invincibility
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

class ModernProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, projectile_type):
        super().__init__()
        self.type = projectile_type
        
        if self.type == "normal":
            self.size = (8, 8)
            self.color = NEON_BLUE
            self.speed = 15
        elif self.type == "special":
            self.size = (12, 12)
            self.color = NEON_PINK
            self.speed = 12
        
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, 
                         (self.size[0]//2, self.size[1]//2), 
                         self.size[0]//2)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.angle = math.radians(angle)
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(
            self.speed * math.sin(self.angle),
            -self.speed * math.cos(self.angle)
        )
        self.particles = ParticleEffect(x, y, self.color)

    def update(self):
        self.position += self.velocity
        self.rect.center = self.position
        self.particles.x = self.rect.centerx
        self.particles.y = self.rect.centery
        self.particles.create_particles(1)
        self.particles.update()
        
        if (self.rect.bottom < -50 or self.rect.top > HEIGHT + 50 or 
            self.rect.right < -50 or self.rect.left > WIDTH + 50):
            self.kill()

class ModernAsteroid(pygame.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.size = size
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Create a more detailed asteroid
        points = []
        num_points = 8
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            radius = size//2 * random.uniform(0.8, 1.2)
            points.append((
                size//2 + radius * math.cos(angle),
                size//2 + radius * math.sin(angle)
            ))
        
        pygame.draw.polygon(self.image, NEON_GREEN, points)
        pygame.draw.polygon(self.image, WHITE, points, 2)
        
        self.rect = self.image.get_rect()
        self.position = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)
        
        # Spawn position and velocity
        if random.random() < 0.5:
            # Spawn on sides
            self.position.x = random.choice([-size, WIDTH + size])
            self.position.y = random.randint(0, HEIGHT)
            self.velocity.x = random.uniform(2, 4) * (-1 if self.position.x > WIDTH else 1)
            self.velocity.y = random.uniform(-2, 2)
        else:
            # Spawn on top/bottom
            self.position.x = random.randint(0, WIDTH)
            self.position.y = random.choice([-size, HEIGHT + size])
            self.velocity.x = random.uniform(-2, 2)
            self.velocity.y = random.uniform(2, 4) * (-1 if self.position.y > HEIGHT else 1)
        
        self.rect.center = self.position

    def update(self):
        self.position += self.velocity
        self.rotation += self.rotation_speed
        
        # Rotate the asteroid
        rotated_image = pygame.transform.rotate(self.image, self.rotation)
        self.rect = rotated_image.get_rect(center=self.position)
        
        # Remove if too far off screen
        if (self.position.x < -100 or self.position.x > WIDTH + 100 or 
            self.position.y < -100 or self.position.y > HEIGHT + 100):
            self.kill()

class ModernGame:
    def __init__(self):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.score = 0
        self.level = 1
        self.background_stars = [
            (random.randint(0, WIDTH), random.randint(0, HEIGHT)) 
            for _ in range(100)
        ]
        self.star_speeds = [random.uniform(0.5, 2) for _ in range(100)]
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()  # Added this line

        # Create player
        self.player = ModernPlayer()
        self.all_sprites.add(self.player)
        
        # Load fonts
        self.title_font = pygame.font.Font(None, 74)
        self.hud_font = pygame.font.Font(None, 36)
        
        # Particle systems
        self.explosion_particles = []

        
    def create_explosion(self, x, y, color):
        particle_effect = ParticleEffect(x, y, color)
        particle_effect.create_particles(20)
        self.explosion_particles.append(particle_effect)
        
    def update_particles(self):
        surviving_particles = []
        for particle_effect in self.explosion_particles:
            particle_effect.update()
            if particle_effect.particles:
                surviving_particles.append(particle_effect)
        self.explosion_particles = surviving_particles
        
    def draw_particles(self):
        for particle_effect in self.explosion_particles:
            particle_effect.draw(self.screen)
            
    def update_background(self):
        for i in range(len(self.background_stars)):
            self.background_stars[i] = (
                (self.background_stars[i][0] - self.star_speeds[i]) % WIDTH,
                self.background_stars[i][1]
            )
            
    def draw_background(self):
        self.screen.fill(SPACE_BLUE)
        for pos, speed in zip(self.background_stars, self.star_speeds):
            alpha = int(255 * (speed / 2))
            star_surface = pygame.Surface((2, 2))
            star_surface.fill(WHITE)
            star_surface.set_alpha(alpha)
            self.screen.blit(star_surface, pos)
            
    def draw_hud(self):
        # Health bar
        health_width = 200
        pygame.draw.rect(self.screen, (60, 60, 60), (20, 20, health_width, 20))
        health_percent = max(0, self.player.health / 100)
        pygame.draw.rect(self.screen, NEON_BLUE, 
                        (20, 20, health_width * health_percent, 20))
        
        # Shield bar
        pygame.draw.rect(self.screen, (60, 60, 60), (20, 45, health_width, 10))
        shield_percent = max(0, self.player.shield / 100)
        pygame.draw.rect(self.screen, NEON_GREEN,
                        (20, 45, health_width * shield_percent, 10))
        
        # Ammo and score
        ammo_text = self.hud_font.render(f'Ammo: {self.player.ammunition}', True, WHITE)
        special_text = self.hud_font.render(f'Special: {self.player.special_ammo}', True, NEON_PINK)
        score_text = self.hud_font.render(f'Score: {self.score}', True, WHITE)
        level_text = self.hud_font.render(f'Level: {self.level}', True, WHITE)
        
        self.screen.blit(ammo_text, (20, 70))
        self.screen.blit(special_text, (20, 100))
        self.screen.blit(score_text, (WIDTH - 150, 20))
        self.screen.blit(level_text, (WIDTH - 150, 50))
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.player.ammunition > 0:
                    self.player.ammunition -= 1
                    projectile = ModernProjectile(
                        self.player.rect.centerx, 
                        self.player.rect.centery,
                        self.player.angle,
                        "normal"
                    )
                    self.all_sprites.add(projectile)
                    self.projectiles.add(projectile)
                elif event.key == pygame.K_q and self.player.special_ammo > 0:
                    self.player.special_ammo -= 1
                    projectile = ModernProjectile(
                        self.player.rect.centerx,
                        self.player.rect.centery,
                        self.player.angle,
                        "special"
                    )
                    self.all_sprites.add(projectile)
                    self.projectiles.add(projectile)
                elif event.key == pygame.K_r and self.game_over:
                    self.__init__()

    def spawn_power_up(self):
        if random.random() < 0.01:  # 1% chance per frame
            power_up = PowerUp(
                random.randint(0, WIDTH),
                -20,
                random.choice(["ammo", "shield", "special"])
            )
            self.all_sprites.add(power_up)
            self.power_ups.add(power_up)

    def update(self):
        if not self.game_over:
            self.all_sprites.update()
            self.update_particles()
            self.update_background()
            
            # Spawn asteroids with increasing frequency and speed
            if len(self.asteroids) < 5 + self.level:
                size = random.randint(30, 60)
                asteroid = ModernAsteroid(size)
                self.all_sprites.add(asteroid)
                self.asteroids.add(asteroid)
            
            # Spawn power-ups
            self.spawn_power_up()
            
            # Check projectile-asteroid collisions
            hits = pygame.sprite.groupcollide(self.projectiles, self.asteroids, True, False)
            for projectile, asteroids_hit in hits.items():
                for asteroid in asteroids_hit:
                    # Create explosion effect
                    self.create_explosion(asteroid.rect.centerx, asteroid.rect.centery, NEON_GREEN)
                    
                    if projectile.type == "special":
                        # Special projectiles destroy asteroids immediately
                        asteroid.kill()
                        self.score += 20
                    else:
                        # Normal projectiles split larger asteroids
                        if asteroid.size > 30:
                            # Split into two smaller asteroids
                            for _ in range(2):
                                new_size = asteroid.size // 2
                                new_asteroid = ModernAsteroid(new_size)
                                new_asteroid.position = pygame.math.Vector2(asteroid.rect.center)
                                new_asteroid.velocity = asteroid.velocity.rotate(random.uniform(-45, 45))
                                self.all_sprites.add(new_asteroid)
                                self.asteroids.add(new_asteroid)
                            asteroid.kill()
                        else:
                            asteroid.kill()
                        self.score += 10
                    
                    if self.score % 100 == 0:
                        self.level += 1
                        # Reward player with special ammo on level up
                        self.player.special_ammo = min(self.player.special_ammo + 1, 5)
            
            # Check player-asteroid collisions
            if self.player.invincibility_timer == 0:
                hits = pygame.sprite.spritecollide(self.player, self.asteroids, True)
                if hits:
                    for asteroid in hits:
                        # Shield takes damage first
                        remaining_damage = asteroid.size
                        if self.player.shield > 0:
                            shield_damage = min(self.player.shield, remaining_damage)
                            self.player.shield -= shield_damage
                            remaining_damage -= shield_damage
                        
                        # Any remaining damage affects health
                        if remaining_damage > 0:
                            self.player.health -= remaining_damage
                        
                        # Create explosion effect
                        self.create_explosion(asteroid.rect.centerx, asteroid.rect.centery, NEON_PINK)
                        
                    self.player.invincibility_timer = 60
                    
                    if self.player.health <= 0:
                        self.game_over = True
                        self.create_explosion(self.player.rect.centerx, self.player.rect.centery, NEON_BLUE)
            
            # Check power-up collisions
            power_up_hits = pygame.sprite.spritecollide(self.player, self.power_ups, True)
            for power_up in power_up_hits:
                if power_up.type == "ammo":
                    self.player.ammunition = min(self.player.ammunition + 20, 100)
                elif power_up.type == "shield":
                    self.player.shield = min(self.player.shield + 50, 100)
                elif power_up.type == "special":
                    self.player.special_ammo = min(self.player.special_ammo + 1, 5)
                
                # Create collection effect
                self.create_explosion(power_up.rect.centerx, power_up.rect.centery, NEON_BLUE)

    def draw(self):
        self.draw_background()
        self.draw_particles()
        
        # Draw engine particles
        self.player.engine_particles.draw(self.screen)
        
        # Draw all sprites
        self.all_sprites.draw(self.screen)
        
        # Draw projectile particles
        for sprite in self.projectiles:
            sprite.particles.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
        
        if self.game_over:
            game_over_text = self.title_font.render('GAME OVER', True, NEON_PINK)
            score_text = self.hud_font.render(f'Final Score: {self.score}', True, WHITE)
            restart_text = self.hud_font.render('Press R to Restart', True, WHITE)
            
            self.screen.blit(game_over_text, 
                           (WIDTH//2 - game_over_text.get_width()//2, 
                            HEIGHT//2 - game_over_text.get_height()))
            self.screen.blit(score_text,
                           (WIDTH//2 - score_text.get_width()//2,
                            HEIGHT//2 + 20))
            self.screen.blit(restart_text,
                           (WIDTH//2 - restart_text.get_width()//2,
                            HEIGHT//2 + 60))
        
        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()

# Power-up class definition
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.power_type = power_type
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        
        if self.power_type == "ammo":
            self.image.fill(NEON_BLUE)
        elif self.power_type == "shield":
            self.image.fill(NEON_GREEN)
        elif self.power_type == "special":
            self.image.fill(NEON_PINK)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = 2

    def update(self):
        self.rect.y += self.velocity
        if self.rect.top > HEIGHT:
            self.kill()


            

# Start the game
if __name__ == "__main__":
    game = ModernGame()
    game.run()
                        
                        
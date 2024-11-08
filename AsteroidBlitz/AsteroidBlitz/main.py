import pygame
import random
import math
from pygame import mixer
import os

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroid Blitz")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, WHITE, [(15, 0), (30, 40), (15, 30), (0, 40)])
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0
        self.speed_y = 0
        self.angle = 0
        self.health = 100
        self.ammunition = 50  # Reduced ammo to emphasize resource management
        self.invincibility_timer = 0

    def update(self):
        # Rotation
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = max(self.speed_x - 0.5, -5)
        if keys[pygame.K_RIGHT]:
            self.speed_x = min(self.speed_x + 0.5, 5)
        if keys[pygame.K_UP]:
            self.speed_y = max(self.speed_y - 0.5, -5)
        if keys[pygame.K_DOWN]:
            self.speed_y = min(self.speed_y + 0.5, 5)
            
        # Apply movement
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
            self.speed_x = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.speed_x = 0
        if self.rect.top < 0:
            self.rect.top = 0
            self.speed_y = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.speed_y = 0
            
        # Friction
        self.speed_x *= 0.95
        self.speed_y *= 0.95

        # Invincibility countdown
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

# Projectile class with different types
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, projectile_type):
        super().__init__()
        self.type = projectile_type
        self.image = pygame.Surface((6, 6))
        if self.type == "laser":
            self.image.fill(RED)
            self.speed = 12
        elif self.type == "explosive":
            self.image.fill(YELLOW)
            self.speed = 8
        else:
            self.image.fill(GREEN)
            self.speed = 10

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.angle = math.radians(angle)
        
    def update(self):
        self.rect.x += self.speed * math.sin(self.angle)
        self.rect.y -= self.speed * math.cos(self.angle)
        if (self.rect.bottom < 0 or self.rect.top > HEIGHT or 
            self.rect.right < 0 or self.rect.left > WIDTH):
            self.kill()

# Asteroid class with behavior modifications
class Asteroid(pygame.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.size = size
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect()
        
        # Random spawn position outside the screen
        side = random.randint(0, 3)
        if side == 0:  # Top
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = -size
        elif side == 1:  # Right
            self.rect.x = WIDTH + size
            self.rect.y = random.randint(0, HEIGHT)
        elif side == 2:  # Bottom
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = HEIGHT + size
        else:  # Left
            self.rect.x = -size
            self.rect.y = random.randint(0, HEIGHT)
            
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        
    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Remove if off screen
        if (self.rect.right < -50 or self.rect.left > WIDTH + 50 or 
            self.rect.bottom < -50 or self.rect.top > HEIGHT + 50):
            self.kill()

# Game class with difficulty scaling and health feedback
class Game:
    def __init__(self):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.score = 0
        self.level = 1
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        
        # Create player
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # Font
        self.font = pygame.font.Font(None, 36)
        
    def spawn_asteroid(self):
        size = random.randint(20, 50)
        asteroid = Asteroid(size)
        self.all_sprites.add(asteroid)
        self.asteroids.add(asteroid)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.player.ammunition > 0:
                    # Use different projectiles based on ammo count
                    if self.player.ammunition % 5 == 0:
                        projectile_type = "explosive"
                    else:
                        projectile_type = "laser"
                    projectile = Projectile(self.player.rect.centerx, self.player.rect.centery, self.player.angle, projectile_type)
                    self.all_sprites.add(projectile)
                    self.projectiles.add(projectile)
                    self.player.ammunition -= 1
                elif event.key == pygame.K_r and self.game_over:
                    self.__init__()
            elif event.type == pygame.MOUSEMOTION:
                # Calculate angle between player and mouse
                mouse_x, mouse_y = event.pos
                rel_x = mouse_x - self.player.rect.centerx
                rel_y = mouse_y - self.player.rect.centery
                self.player.angle = math.degrees(math.atan2(rel_x, -rel_y))
                
    def update(self):
        if not self.game_over:
            self.all_sprites.update()
            
            # Spawn asteroids with increasing frequency
            if len(self.asteroids) < 5 + self.level:
                self.spawn_asteroid()
                
            # Check collisions
            hits = pygame.sprite.groupcollide(self.projectiles, self.asteroids, True, True)
            for hit in hits:
                self.score += 10
                if self.score % 100 == 0:
                    self.level += 1
            
            hits = pygame.sprite.spritecollide(self.player, self.asteroids, True)
            for hit in hits:
                if self.player.invincibility_timer == 0:
                    self.player.health -= hit.size
                    self.player.invincibility_timer = 60  # Temporary invincibility
                if self.player.health <= 0:
                    self.game_over = True
                    
    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        
        # Draw HUD with health and ammo feedback
        health_text = self.font.render(f'Health: {self.player.health}', True, WHITE)
        ammo_text = self.font.render(f'Ammo: {self.player.ammunition}', True, WHITE)
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        level_text = self.font.render(f'Level: {self.level}', True, WHITE)
        
        self.screen.blit(health_text, (10, 10))
        self.screen.blit(ammo_text, (10, 40))
        self.screen.blit(score_text, (10, 70))
        self.screen.blit(level_text, (10, 100))
        
        if self.game_over:
            game_over_text = self.font.render('Game Over! Press R to restart', True, RED)
            self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
        
        pygame.display.flip()
        
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()

# Start the game
game = Game()
game.run()

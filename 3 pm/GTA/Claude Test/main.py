import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
BROWN = (139, 69, 19)

class Car:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.max_speed = 5
        self.acceleration = 0.2
        self.rotation_speed = 3
        self.color = color
        self.width = 30
        self.height = 20
        self.health = 100
        
    def update(self, keys):
        # Handle input
        if keys[pygame.K_UP]:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN]:
            self.speed = max(self.speed - self.acceleration, -self.max_speed/2)
        else:
            self.speed *= 0.95
            
        if abs(self.speed) > 0.1:
            if keys[pygame.K_LEFT]:
                self.angle += self.rotation_speed
            if keys[pygame.K_RIGHT]:
                self.angle -= self.rotation_speed
                
        # Update position
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y -= self.speed * math.sin(math.radians(self.angle))
        
        # Keep car on screen
        self.x = max(self.width/2, min(SCREEN_WIDTH - self.width/2, self.x))
        self.y = max(self.height/2, min(SCREEN_HEIGHT - self.height/2, self.y))
        
    def draw(self, screen):
        # Create car surface
        car_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        car_surface.fill(self.color)
        
        # Add windshield
        pygame.draw.rect(car_surface, (100, 100, 255), 
                        (self.width//3, 2, self.width//3, self.height//3))
        
        # Rotate and draw
        rotated = pygame.transform.rotate(car_surface, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        screen.blit(rotated, rect)
        
    def get_rect(self):
        return pygame.Rect(self.x - self.width/2, self.y - self.height/2, 
                          self.width, self.height)

class Pedestrian:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(0.5, 1.5)
        self.direction = random.uniform(0, 360)
        self.radius = 8
        self.color = random.choice([BROWN, BLACK, WHITE])
        self.wander_timer = 0
        
    def update(self):
        # Random wandering
        self.wander_timer -= 1
        if self.wander_timer <= 0:
            self.direction = random.uniform(0, 360)
            self.wander_timer = random.randint(60, 180)
            
        # Move
        self.x += self.speed * math.cos(math.radians(self.direction))
        self.y += self.speed * math.sin(math.radians(self.direction))
        
        # Bounce off edges
        if self.x <= self.radius or self.x >= SCREEN_WIDTH - self.radius:
            self.direction = 180 - self.direction
        if self.y <= self.radius or self.y >= SCREEN_HEIGHT - self.radius:
            self.direction = -self.direction
            
        # Keep on screen
        self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.y))
        
    def draw(self, screen):
        # Draw body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Draw head
        pygame.draw.circle(screen, (255, 220, 177), 
                          (int(self.x), int(self.y - self.radius//2)), self.radius//2)
        
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                          self.radius * 2, self.radius * 2)

class Building:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = random.choice([GRAY, DARK_GRAY, (100, 100, 100)])
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        # Draw windows
        window_size = 10
        padding = 15
        for wx in range(self.rect.x + padding, self.rect.x + self.rect.width - padding, 20):
            for wy in range(self.rect.y + padding, self.rect.y + self.rect.height - padding, 20):
                pygame.draw.rect(screen, YELLOW if random.random() > 0.3 else BLACK,
                               (wx, wy, window_size, window_size))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("GTA Python")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game objects
        self.player_car = Car(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, RED)
        self.pedestrians = []
        self.buildings = []
        self.traffic_cars = []
        self.score = 0
        self.wanted_level = 0
        
        # Create city
        self.create_city()
        
        # Spawn pedestrians
        for _ in range(15):
            while True:
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = random.randint(50, SCREEN_HEIGHT - 50)
                valid = True
                for building in self.buildings:
                    if building.rect.collidepoint(x, y):
                        valid = False
                        break
                if valid:
                    self.pedestrians.append(Pedestrian(x, y))
                    break
                    
        # Spawn traffic
        for _ in range(5):
            while True:
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = random.randint(100, SCREEN_HEIGHT - 100)
                valid = True
                for building in self.buildings:
                    if building.rect.collidepoint(x, y):
                        valid = False
                        break
                if valid:
                    car = Car(x, y, random.choice([BLUE, GREEN, YELLOW, WHITE]))
                    car.angle = random.randint(0, 360)
                    self.traffic_cars.append(car)
                    break
                    
    def create_city(self):
        # Create building blocks
        building_positions = [
            (50, 50, 150, 100),
            (250, 50, 100, 150),
            (400, 50, 150, 100),
            (600, 50, 100, 100),
            (750, 50, 150, 150),
            
            (50, 250, 100, 100),
            (200, 200, 150, 150),
            (400, 250, 100, 100),
            (600, 200, 150, 150),
            (800, 250, 100, 100),
            
            (50, 450, 150, 150),
            (250, 500, 100, 100),
            (400, 450, 150, 150),
            (600, 500, 100, 100),
            (750, 450, 150, 150),
        ]
        
        for x, y, w, h in building_positions:
            self.buildings.append(Building(x, y, w, h))
            
    def handle_collisions(self):
        # Check pedestrian collisions
        for ped in self.pedestrians[:]:
            if self.player_car.get_rect().colliderect(ped.get_rect()):
                if abs(self.player_car.speed) > 2:
                    self.pedestrians.remove(ped)
                    self.score += 100
                    self.wanted_level = min(self.wanted_level + 1, 5)
                    
        # Check building collisions
        player_rect = self.player_car.get_rect()
        for building in self.buildings:
            if player_rect.colliderect(building.rect):
                # Bounce back
                self.player_car.speed = -self.player_car.speed * 0.5
                self.player_car.x -= self.player_car.speed * math.cos(math.radians(self.player_car.angle)) * 5
                self.player_car.y += self.player_car.speed * math.sin(math.radians(self.player_car.angle)) * 5
                
    def update_traffic(self):
        for car in self.traffic_cars:
            # Simple AI - move forward and turn randomly
            car.speed = 2
            if random.random() < 0.02:
                car.angle += random.choice([-45, 45])
                
            # Update position
            car.x += car.speed * math.cos(math.radians(car.angle))
            car.y -= car.speed * math.sin(math.radians(car.angle))
            
            # Bounce off screen edges
            if car.x <= 0 or car.x >= SCREEN_WIDTH:
                car.angle = 180 - car.angle
            if car.y <= 0 or car.y >= SCREEN_HEIGHT:
                car.angle = -car.angle
                
            # Keep on screen
            car.x = max(car.width/2, min(SCREEN_WIDTH - car.width/2, car.x))
            car.y = max(car.height/2, min(SCREEN_HEIGHT - car.height/2, car.y))
            
    def draw_hud(self):
        # Score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Wanted level
        wanted_text = font.render("Wanted: ", True, WHITE)
        self.screen.blit(wanted_text, (10, 50))
        for i in range(self.wanted_level):
            pygame.draw.polygon(self.screen, YELLOW,
                              [(120 + i*30, 55), (130 + i*30, 50), 
                               (135 + i*30, 60), (125 + i*30, 65),
                               (115 + i*30, 60)])
                               
        # Controls
        font_small = pygame.font.Font(None, 24)
        controls = [
            "Arrow Keys - Drive",
            "ESC - Quit"
        ]
        for i, control in enumerate(controls):
            control_text = font_small.render(control, True, WHITE)
            self.screen.blit(control_text, (SCREEN_WIDTH - 150, 10 + i*25))
            
    def run(self):
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        
            # Get keys
            keys = pygame.key.get_pressed()
            
            # Update
            self.player_car.update(keys)
            for ped in self.pedestrians:
                ped.update()
            self.update_traffic()
            self.handle_collisions()
            
            # Decrease wanted level over time
            if random.random() < 0.005 and self.wanted_level > 0:
                self.wanted_level -= 1
                
            # Draw
            self.screen.fill((50, 50, 50))  # Dark gray background
            
            # Draw roads (simple grid)
            for x in range(0, SCREEN_WIDTH, 200):
                pygame.draw.line(self.screen, DARK_GRAY, (x, 0), (x, SCREEN_HEIGHT), 50)
            for y in range(0, SCREEN_HEIGHT, 200):
                pygame.draw.line(self.screen, DARK_GRAY, (0, y), (SCREEN_WIDTH, y), 50)
                
            # Draw buildings
            for building in self.buildings:
                building.draw(self.screen)
                
            # Draw pedestrians
            for ped in self.pedestrians:
                ped.draw(self.screen)
                
            # Draw traffic
            for car in self.traffic_cars:
                car.draw(self.screen)
                
            # Draw player
            self.player_car.draw(self.screen)
            
            # Draw HUD
            self.draw_hud()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
import pygame
import sys
import math

# --- 1. SETTINGS & CONSTANTS ---
pygame.init()

TILE_SIZE = 40  
FPS = 60        

# Colors (RGB)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

# We rename this to ORIGINAL_MAP so we always have a fresh copy to load from
ORIGINAL_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 1, 1, 2, 1, 2, 1, 1, 1, 0, 1, 1, 1, 1],
    [2, 2, 2, 1, 0, 1, 2, 2, 2, 2, 2, 2, 2, 1, 0, 1, 2, 2, 2],
    [1, 1, 1, 1, 0, 1, 2, 1, 1, 2, 1, 1, 2, 1, 0, 1, 1, 1, 1], 
    [2, 2, 2, 2, 0, 2, 2, 1, 2, 2, 2, 1, 2, 2, 0, 2, 2, 2, 2], 
    [1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1],
    [2, 2, 2, 1, 0, 1, 2, 2, 2, 2, 2, 2, 2, 1, 0, 1, 2, 2, 2],
    [1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Create our active map by copying the original
LEVEL_MAP = [[tile for tile in row] for row in ORIGINAL_MAP]

COLS = len(LEVEL_MAP[0])
ROWS = len(LEVEL_MAP)
WIDTH = COLS * TILE_SIZE

# We add 50 pixels to the HEIGHT to make room for the score text at the bottom
UI_HEIGHT = 50 
HEIGHT = (ROWS * TILE_SIZE) + UI_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man: Smooth Movement & Scoring")
clock = pygame.time.Clock()

# Set up the font for our score text
font = pygame.font.SysFont("Arial", 28, bold=True)


# --- 2. THE PLAYER CLASS ---
class Player:
    def __init__(self, start_col, start_row):
        self.x = (start_col * TILE_SIZE) + (TILE_SIZE // 2)
        self.y = (start_row * TILE_SIZE) + (TILE_SIZE // 2)
        
        self.speed = 2  
        self.dx = 0     
        self.dy = 0     
        
        self.queued_dx = 0
        self.queued_dy = 0
        
        self.direction = 0
        self.anim_counter = 0
        
        # NEW: Track score!
        self.score = 0

    def reset_position(self):
        # Sends Pac-Man back to the top left, but keeps his score
        self.x = (1 * TILE_SIZE) + (TILE_SIZE // 2)
        self.y = (1 * TILE_SIZE) + (TILE_SIZE // 2)
        self.dx = 0
        self.dy = 0
        self.queued_dx = 0
        self.queued_dy = 0
        self.direction = 0

    def update(self, keys):
        # 1. Update Queue
        if keys[pygame.K_LEFT]:  
            self.queued_dx = -self.speed; self.queued_dy = 0
        elif keys[pygame.K_RIGHT]: 
            self.queued_dx = self.speed; self.queued_dy = 0
        elif keys[pygame.K_UP]:    
            self.queued_dx = 0; self.queued_dy = -self.speed
        elif keys[pygame.K_DOWN]:  
            self.queued_dx = 0; self.queued_dy = self.speed

        # 2. Instant Reversal
        if self.queued_dx != 0 and self.queued_dx == -self.dx:
            self.dx = self.queued_dx; self.dy = 0
            self.direction = math.pi if self.dx < 0 else 0
        if self.queued_dy != 0 and self.queued_dy == -self.dy:
            self.dx = 0; self.dy = self.queued_dy
            self.direction = 3 * math.pi / 2 if self.dy < 0 else math.pi / 2

        # 3. Grid Alignment & Turning
        at_center_x = (self.x % TILE_SIZE) == (TILE_SIZE // 2)
        at_center_y = (self.y % TILE_SIZE) == (TILE_SIZE // 2)

        if at_center_x and at_center_y:
            col = int(self.x // TILE_SIZE)
            row = int(self.y // TILE_SIZE)

            q_col = (col + (1 if self.queued_dx > 0 else -1 if self.queued_dx < 0 else 0)) % COLS
            q_row = row + (1 if self.queued_dy > 0 else -1 if self.queued_dy < 0 else 0)
            
            if LEVEL_MAP[q_row][q_col] != 1:
                self.dx = self.queued_dx
                self.dy = self.queued_dy
                
                if self.dx > 0: self.direction = 0
                elif self.dx < 0: self.direction = math.pi
                elif self.dy > 0: self.direction = math.pi / 2
                elif self.dy < 0: self.direction = 3 * math.pi / 2
            else:
                curr_col = (col + (1 if self.dx > 0 else -1 if self.dx < 0 else 0)) % COLS
                curr_row = row + (1 if self.dy > 0 else -1 if self.dy < 0 else 0)
                
                if LEVEL_MAP[curr_row][curr_col] == 1:
                    self.dx = 0
                    self.dy = 0

        # 4. Apply movement
        self.x += self.dx
        self.y += self.dy

        # 5. Screen wrap-around 
        if self.x < 0: self.x += WIDTH
        elif self.x > WIDTH: self.x -= WIDTH

        # 6. Eating Logic & Win Condition!
        current_col = int(self.x // TILE_SIZE)
        current_row = int(self.y // TILE_SIZE)
        
        if LEVEL_MAP[current_row][current_col] == 0:
            LEVEL_MAP[current_row][current_col] = 2 # Eat the pellet
            self.score += 10 # Increase score
            
            # Check if there are any pellets left in the whole map
            pellets_left = any(0 in row for row in LEVEL_MAP)
            
            if not pellets_left:
                # If no pellets are left, refresh the map from the master copy!
                for r in range(ROWS):
                    for c in range(COLS):
                        LEVEL_MAP[r][c] = ORIGINAL_MAP[r][c]
                
                # Send player back to the start
                self.reset_position()

    def draw(self, surface):
        radius = (TILE_SIZE // 2) - 4
        
        if self.dx != 0 or self.dy != 0:
            self.anim_counter += 0.3 
            mouth_angle = abs(math.sin(self.anim_counter)) * (math.pi / 4)
        else:
            mouth_angle = math.pi / 6 

        start_angle = self.direction + mouth_angle
        end_angle = self.direction + (2 * math.pi) - mouth_angle

        points = [(self.x, self.y)]
        steps = 15 
        angle_step = (end_angle - start_angle) / steps
        
        for i in range(steps + 1):
            current_angle = start_angle + (i * angle_step)
            arc_x = self.x + radius * math.cos(current_angle)
            arc_y = self.y + radius * math.sin(current_angle)
            points.append((arc_x, arc_y))

        pygame.draw.polygon(surface, YELLOW, points)


# --- 3. MAIN GAME SETUP ---
player = Player(1, 1)

# --- 4. GAME LOOP ---
running = True
while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    keys = pygame.key.get_pressed()
    player.update(keys)

    # 2. Drawing
    screen.fill(BLACK) 

    # Draw the map
    for row_idx, row in enumerate(LEVEL_MAP):
        for col_idx, tile in enumerate(row):
            if tile == 1:
                rect_x = col_idx * TILE_SIZE
                rect_y = row_idx * TILE_SIZE
                wall_rect = pygame.Rect(rect_x, rect_y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, BLUE, wall_rect, 2)
            elif tile == 0:
                pellet_x = (col_idx * TILE_SIZE) + (TILE_SIZE // 2)
                pellet_y = (row_idx * TILE_SIZE) + (TILE_SIZE // 2)
                pygame.draw.circle(screen, WHITE, (pellet_x, pellet_y), 4) 

    # Draw the player
    player.draw(screen)

    # Draw the UI/Score
    # Render the text into an image, then blit it to the bottom of the screen
    score_text = font.render(f"SCORE: {player.score}", True, WHITE)
    screen.blit(score_text, (10, ROWS * TILE_SIZE + 10))

    # 3. Update Display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
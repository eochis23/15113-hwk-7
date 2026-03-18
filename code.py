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

# Adding the iconic ghost colors
RED = (255, 0, 0)      # Blinky
PINK = (255, 182, 193) # Pinky
CYAN = (0, 255, 255)   # Inky
ORANGE = (255, 165, 0) # Clyde

# Master map copy
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
    [2, 2, 2, 2, 0, 2, 2, 1, 2, 2, 2, 1, 2, 2, 0, 2, 2, 2, 2], # Row 9, Col 9 is center house
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

LEVEL_MAP = [[tile for tile in row] for row in ORIGINAL_MAP]
COLS = len(LEVEL_MAP[0])
ROWS = len(LEVEL_MAP)
WIDTH = COLS * TILE_SIZE
UI_HEIGHT = 50 
HEIGHT = (ROWS * TILE_SIZE) + UI_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man: The Full Squad")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 28, bold=True)


# --- 2. THE PLAYER CLASS ---
class Player:
    def __init__(self, start_col, start_row):
        self.x = (start_col * TILE_SIZE) + (TILE_SIZE // 2)
        self.y = (start_row * TILE_SIZE) + (TILE_SIZE // 2)
        self.speed = 2  
        self.dx = 0; self.dy = 0     
        self.queued_dx = 0; self.queued_dy = 0
        self.direction = 0
        self.anim_counter = 0
        self.score = 0

    def reset_position(self):
        self.x = (1 * TILE_SIZE) + (TILE_SIZE // 2)
        self.y = (1 * TILE_SIZE) + (TILE_SIZE // 2)
        self.dx = 0; self.dy = 0
        self.queued_dx = 0; self.queued_dy = 0
        self.direction = 0

    def update(self, keys):
        if keys[pygame.K_LEFT]:  
            self.queued_dx = -self.speed; self.queued_dy = 0
        elif keys[pygame.K_RIGHT]: 
            self.queued_dx = self.speed; self.queued_dy = 0
        elif keys[pygame.K_UP]:    
            self.queued_dx = 0; self.queued_dy = -self.speed
        elif keys[pygame.K_DOWN]:  
            self.queued_dx = 0; self.queued_dy = self.speed

        if self.queued_dx != 0 and self.queued_dx == -self.dx:
            self.dx = self.queued_dx; self.dy = 0
            self.direction = math.pi if self.dx < 0 else 0
        if self.queued_dy != 0 and self.queued_dy == -self.dy:
            self.dx = 0; self.dy = self.queued_dy
            self.direction = 3 * math.pi / 2 if self.dy < 0 else math.pi / 2

        at_center_x = (self.x % TILE_SIZE) == (TILE_SIZE // 2)
        at_center_y = (self.y % TILE_SIZE) == (TILE_SIZE // 2)

        if at_center_x and at_center_y:
            col = int(self.x // TILE_SIZE); row = int(self.y // TILE_SIZE)
            q_col = (col + (1 if self.queued_dx > 0 else -1 if self.queued_dx < 0 else 0)) % COLS
            q_row = row + (1 if self.queued_dy > 0 else -1 if self.queued_dy < 0 else 0)
            
            if LEVEL_MAP[q_row][q_col] != 1:
                self.dx = self.queued_dx; self.dy = self.queued_dy
                if self.dx > 0: self.direction = 0
                elif self.dx < 0: self.direction = math.pi
                elif self.dy > 0: self.direction = math.pi / 2
                elif self.dy < 0: self.direction = 3 * math.pi / 2
            else:
                curr_col = (col + (1 if self.dx > 0 else -1 if self.dx < 0 else 0)) % COLS
                curr_row = row + (1 if self.dy > 0 else -1 if self.dy < 0 else 0)
                if LEVEL_MAP[curr_row][curr_col] == 1:
                    self.dx = 0; self.dy = 0

        self.x += self.dx; self.y += self.dy
        if self.x < 0: self.x += WIDTH
        elif self.x > WIDTH: self.x -= WIDTH

        current_col = int(self.x // TILE_SIZE); current_row = int(self.y // TILE_SIZE)
        if LEVEL_MAP[current_row][current_col] == 0:
            LEVEL_MAP[current_row][current_col] = 2 
            self.score += 10 
            if not any(0 in row for row in LEVEL_MAP):
                for r in range(ROWS):
                    for c in range(COLS): LEVEL_MAP[r][c] = ORIGINAL_MAP[r][c]
                self.reset_position()

    def draw(self, surface):
        radius = (TILE_SIZE // 2) - 4
        if self.dx != 0 or self.dy != 0:
            self.anim_counter += 0.3 
            mouth_angle = abs(math.sin(self.anim_counter)) * (math.pi / 4)
        else: mouth_angle = math.pi / 6 
        start_angle = self.direction + mouth_angle
        end_angle = self.direction + (2 * math.pi) - mouth_angle
        points = [(self.x, self.y)]
        steps = 15 
        for i in range(steps + 1):
            current_angle = start_angle + (i * ((end_angle - start_angle) / steps))
            points.append((self.x + radius * math.cos(current_angle), self.y + radius * math.sin(current_angle)))
        pygame.draw.polygon(surface, YELLOW, points)


# --- 3. THE GHOST CLASS ---
class Ghost:
    def __init__(self, start_col, start_row, color, name, spawn_delay_frames):
        self.x = (start_col * TILE_SIZE) + (TILE_SIZE // 2)
        self.y = (start_row * TILE_SIZE) + (TILE_SIZE // 2)
        
        # Save home coordinates for Clyde's coward logic
        self.home_col = start_col
        self.home_row = start_row
        
        self.color = color
        self.name = name # Blinky, Pinky, Inky, Clyde
        self.speed = 2 
        
        # New State variables: 'trapped', 'exiting', 'chasing'
        self.state = 'trapped'
        self.spawn_timer = spawn_delay_frames
        
        self.dx = 0; self.dy = 0

    def update(self, target_player, blinky_ref):
        # 1. Ghost House Logic
        if self.state == 'trapped':
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                self.state = 'exiting'
            return # Don't move while trapped
            
        if self.state == 'exiting':
            # Force them to Row 7, Col 9 (Just outside the door)
            exit_x = (9 * TILE_SIZE) + (TILE_SIZE // 2)
            exit_y = (7 * TILE_SIZE) + (TILE_SIZE // 2)
            
            # Move towards exit pixel by pixel
            if self.x < exit_x: self.dx = self.speed; self.dy = 0
            elif self.x > exit_x: self.dx = -self.speed; self.dy = 0
            elif self.y > exit_y: self.dx = 0; self.dy = -self.speed
            else:
                # We have reached the exit! Start hunting.
                self.state = 'chasing'
            
            self.x += self.dx; self.y += self.dy
            return # Skip normal targeting while exiting

        # 2. Normal Pathfinding Logic (Only at tile center)
        at_center_x = (self.x % TILE_SIZE) == (TILE_SIZE // 2)
        at_center_y = (self.y % TILE_SIZE) == (TILE_SIZE // 2)

        if at_center_x and at_center_y:
            col = int(self.x // TILE_SIZE); row = int(self.y // TILE_SIZE)
            
            # --- GET TARGET TILE BASED ON PERSONALITY ---
            p_col = int(target_player.x // TILE_SIZE)
            p_row = int(target_player.y // TILE_SIZE)
            
            t_col, t_row = p_col, p_row # Default target (Blinky logic)

            if self.name == "Pinky":
                # Aim 4 tiles in front of Pac-Man (Ambush)
                p_dx = target_player.dx // target_player.speed if target_player.dx != 0 else 0
                p_dy = target_player.dy // target_player.speed if target_player.dy != 0 else 0
                t_col = p_col + (p_dx * 4); t_row = p_row + (p_dy * 4)

            elif self.name == "Inky":
                # Vector Logic (Flank). Target is complex based on Blinky and Pac-Man.
                p_dx = target_player.dx // target_player.speed if target_player.dx != 0 else 0
                p_dy = target_player.dy // target_player.speed if target_player.dy != 0 else 0
                
                # Point 2 tiles ahead of Pac-Man
                pivot_col = p_col + (p_dx * 2); pivot_row = p_row + (p_dy * 2)
                
                # Get Blinky's current tile
                b_col = int(blinky_ref.x // TILE_SIZE); b_row = int(blinky_ref.y // TILE_SIZE)
                
                # Vector from Blinky to Pivot, then double it.
                t_col = pivot_col + (pivot_col - b_col); t_row = pivot_row + (pivot_row - b_row)

            elif self.name == "Clyde":
                # Coward Logic. Direct chase if far, run home if close.
                dist_sq = (col - p_col)**2 + (row - p_row)**2
                if dist_sq < 64: # If within 8 tiles (8^2 = 64)
                    t_col, t_row = 0, ROWS - 1 # Go to bottom-left corner

            # --- CALCULATE BEST MOVE ---
            possible_moves = [
                (0, -self.speed, col, row - 1),           # UP
                (-self.speed, 0, (col - 1) % COLS, row),  # LEFT
                (0, self.speed, col, row + 1),            # DOWN
                (self.speed, 0, (col + 1) % COLS, row)     # RIGHT
            ]

            valid_moves = []
            for move_dx, move_dy, n_col, n_row in possible_moves:
                if LEVEL_MAP[n_row][n_col] == 1: continue # Wall
                if move_dx != 0 and move_dx == -self.dx: continue # U-Turn X
                if move_dy != 0 and move_dy == -self.dy: continue # U-Turn Y
                
                # Standard distance formula
                distance = (n_col - t_col)**2 + (n_row - t_row)**2
                valid_moves.append((distance, move_dx, move_dy))

            if valid_moves:
                # Sort by distance and pick the shortest path
                valid_moves.sort(key=lambda x: x[0])
                self.dx = valid_moves[0][1]; self.dy = valid_moves[0][2]

        # Apply movement and screen wrap
        self.x += self.dx; self.y += self.dy
        if self.x < 0: self.x += WIDTH
        elif self.x > WIDTH: self.x -= WIDTH

    def draw(self, surface):
        # --- NEW POLYGON DRAWING LOGIC ---
        # The classic dome-head, squiggly-bottom shape.
        # These are points relative to the ghost's center (0,0)
        body_points = [
            (-14, 4),   # Left "hip"
            (-14, -6),  # Start of dome
            (-10, -12), 
            (-4, -15),  # Top of dome
            (4, -15),
            (10, -12),
            (14, -6),
            (14, 4),    # Right "hip"
            (10, 15),   # Bottom-right foot
            (5, 10),    # Right standard wave
            (0, 15),    # Middle foot
            (-5, 10),   # Left standard wave
            (-10, 15)   # Bottom-left foot
        ]
        
        # Translate the relative points to absolute pixel coordinates
        real_points = [(self.x + px, self.y + py) for px, py in body_points]
        
        # Draw the solid body polygon
        pygame.draw.polygon(surface, self.color, real_points)
        
        # Add some simple eyes so we know which way they are aiming
        eye_color = WHITE
        iris_color = BLUE
        left_eye_pos = (self.x - 6, self.y - 4)
        right_eye_pos = (self.x + 6, self.y - 4)
        
        # Draw whites
        pygame.draw.circle(surface, eye_color, left_eye_pos, 4)
        pygame.draw.circle(surface, eye_color, right_eye_pos, 4)
        
        # Shift iris based on movement direction
        iris_x = 2 if self.dx > 0 else -2 if self.dx < 0 else 0
        iris_y = 2 if self.dy > 0 else -2 if self.dy < 0 else 0
        
        pygame.draw.circle(surface, iris_color, (left_eye_pos[0] + iris_x, left_eye_pos[1] + iris_y), 2)
        pygame.draw.circle(surface, iris_color, (right_eye_pos[0] + iris_x, right_eye_pos[1] + iris_y), 2)


# --- 4. MAIN GAME SETUP ---
player = Player(1, 1)

# Initialize all four ghosts with distinct personalities and spawn delays (FPS * seconds)
blinky = Ghost(9, 9, RED, "Blinky", 0)           # Immediate release
pinky =  Ghost(9, 9, PINK, "Pinky", FPS * 2)     # 2 second delay
inky =   Ghost(8, 9, CYAN, "Inky", FPS * 4)       # 4 second delay
clyde =  Ghost(10, 9, ORANGE, "Clyde", FPS * 6)  # 6 second delay

ghosts = [blinky, pinky, inky, clyde]

# --- 5. GAME LOOP ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    keys = pygame.key.get_pressed()
    player.update(keys)
    
    # Update all ghosts, passing the required references for their AI
    for ghost in ghosts:
        ghost.update(player, blinky)

    # Drawing
    screen.fill(BLACK) 

    # Draw the map
    for row_idx, row in enumerate(LEVEL_MAP):
        for col_idx, tile in enumerate(row):
            if tile == 1:
                wall_rect = pygame.Rect(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, BLUE, wall_rect, 2)
            elif tile == 0:
                pygame.draw.circle(screen, WHITE, (col_idx * TILE_SIZE + TILE_SIZE // 2, row_idx * TILE_SIZE + TILE_SIZE // 2), 4) 

    player.draw(screen)
    for ghost in ghosts:
        ghost.draw(screen)

    score_text = font.render(f"SCORE: {player.score}", True, WHITE)
    screen.blit(score_text, (10, ROWS * TILE_SIZE + 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
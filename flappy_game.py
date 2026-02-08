import pygame
import random

#cstes

WIDTH, HEIGHT = 600,600
GRAVITY = 0.45
FLAP_STRENGTH = -7
PIPE_SPEED = -3
PIPE_DISTANCE = 250
PIPE_GAP = 140
MAX_VELOCITY = 13

print();print()
DEBUG_SCORE = False

# objects

class Bird:
    def __init__(self):
        self.x = 50
        self.y = HEIGHT //2
        self.vel = 0
        self.radius = 20
        self.alive = True
        self.score = 0

    def flap(self):
        self.vel = FLAP_STRENGTH

    def update(self):
        self.vel += GRAVITY
        
        if self.vel > MAX_VELOCITY:
            self.vel = MAX_VELOCITY
        if self.vel < -MAX_VELOCITY:
            self.vel = -MAX_VELOCITY
        self.y += self.vel

        if self.y <= 0 or self.y >= HEIGHT or self.score >= 1000:
            self.alive = False

class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(100, HEIGHT - 100)
        self.passed = False

    def update(self):
        self.x += PIPE_SPEED

    def collides(self, bird):
        bird_left = bird.x - bird.radius
        bird_right = bird.x + bird.radius
        pipe_left = self.x
        pipe_right = self.x + 50

        if bird_right > pipe_left and bird_left < pipe_right:
            gap_top = self.gap_y - PIPE_GAP // 2
            gap_bottom = self.gap_y + PIPE_GAP // 2

            bird_top = bird.y - bird.radius
            bird_bottom = bird.y + bird.radius

            if bird_top < gap_top or bird_bottom > gap_bottom:
                return True

        return False
    
# environment

class FlappyGame:
    def __init__(self, render=True, show_inputs=True):
        self.render = render
        self.show_inputs = show_inputs

        if render:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            self.clock = pygame.time.Clock()
        else:
            self.screen = None
            self.clock = None

        self.input_state = []
        self.reset()

    def reset(self):
        self.bird = Bird()
        self.pipes = [Pipe(WIDTH + 100)]
        self.frame = 0
        self.fitness = 0
        self.input_state = self.get_state()
        return self.input_state
    
    def get_state(self):
        pipe1 = self.pipes[0]
        pipe2 = self.pipes[1] if len(self.pipes) > 1 else pipe1
        state = [ # normalized inputs for neat 
            self.bird.y / HEIGHT,                  # relative height
            self.bird.vel / MAX_VELOCITY,          # relative velocity
            (pipe1.x - self.bird.x) / WIDTH,       # first pipe distance
            (pipe1.gap_y - PIPE_GAP//2) / HEIGHT,  # first pipe gap top
            (pipe1.gap_y + PIPE_GAP//2) / HEIGHT,  # first pipe gap bot
            (pipe2.x - self.bird.x) / WIDTH,       # next pipe distance
            (pipe2.gap_y - PIPE_GAP//2) / HEIGHT,  # next pipe gap top
            (pipe2.gap_y + PIPE_GAP//2) / HEIGHT,  # next pipe gap bot
        ]
        self.input_state = state
        return state
    
    def step(self, action):
        if action:
            self.bird.flap()

        self.bird.update()

        for pipe in self.pipes:
            pipe.update()
            if pipe.collides(self.bird):
                self.bird.alive = False

        # nouveau pipe
        if self.pipes[-1].x < WIDTH - PIPE_DISTANCE:
            self.pipes.append(Pipe(WIDTH))

        # score and remove pipe
        if self.bird.x > self.pipes[0].x + 50:
            self.bird.score += 1
            self.pipes.pop(0)

        self.frame += 1

        done = not self.bird.alive
        return self.get_state(), done
    
    def draw_debug(self):
        if not self.show_inputs or not self.render:
            return
        
        font = pygame.font.SysFont('Arial', 14)
        small_font = pygame.font.SysFont('Arial', 11)
        
        # Draw background panel
        panel_width = 220
        panel_height = 270  # Increased height for more text
        panel_x = WIDTH - panel_width - 10
        panel_y = 10
        
        # Semi-transparent background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))  # Black with transparency
        self.screen.blit(panel_surface, (panel_x, panel_y))
        
        # Draw border
        pygame.draw.rect(self.screen, (255, 255, 255), 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Draw title
        title = font.render("Neural Network Inputs", True, (255, 255, 255))
        self.screen.blit(title, (panel_x + 10, panel_y + 5))
        
        # Input names
        input_names = [
            "Bird Y Position",
            "Bird Velocity",
            "Pipe 1 Distance",
            "Pipe 1 Gap Top",
            "Pipe 1 Gap Bottom",
            "Pipe 2 Distance",
            "Pipe 2 Gap Top",
            "Pipe 2 Gap Bottom"
        ]
        
        y_offset = 35
        bar_width = 120
        bar_height = 10
        
        for i, (name, value) in enumerate(zip(input_names, self.input_state)):
            # Draw input name
            name_surface = small_font.render(name, True, (255, 255, 255))
            self.screen.blit(name_surface, (panel_x + 10, panel_y + y_offset))
            
            # Draw value text
            if i in [0, 2, 3, 4, 5, 6, 7]:  # Values that should be 0-1
                value_text = f"{value:.3f}"
            elif i == 1:  # Velocity (-1 to 1)
                value_text = f"{value:+.3f}"  # Show + or - sign
            else:
                value_text = f"{value:.3f}"
                
            value_surface = small_font.render(value_text, True, (255, 255, 255))
            self.screen.blit(value_surface, (panel_x + 180, panel_y + y_offset))
            
            # For velocity (input 1), draw special bar from -1 to 1
            if i == 1:  # Bird velocity
                bar_x = panel_x + 10
                bar_y = panel_y + y_offset + 18
                
                # Background bar
                pygame.draw.rect(self.screen, (100, 100, 100), 
                               (bar_x, bar_y, bar_width, bar_height))
                
                # Draw center line
                center_x = bar_x + bar_width // 2
                pygame.draw.line(self.screen, (200, 200, 200),
                               (center_x, bar_y - 3),
                               (center_x, bar_y + bar_height + 3), 2)
                
                # Draw velocity bar (from -1 to 1)
                # Map -1 to left edge, 0 to center, 1 to right edge
                fill_center = bar_x + bar_width // 2
                fill_width = int(abs(value) * (bar_width // 2))
                
                if value > 0:  # Positive velocity (going down)
                    fill_start = fill_center
                    fill_end = fill_center + min(fill_width, bar_width // 2)
                    color = (255, 100, 100)  # Red for downward
                else:  # Negative velocity (going up)
                    fill_start = fill_center - min(fill_width, bar_width // 2)
                    fill_end = fill_center
                    color = (100, 255, 100)  # Green for upward
                
                pygame.draw.rect(self.screen, color,
                               (fill_start, bar_y, fill_end - fill_start, bar_height))
                
                # Draw border
                pygame.draw.rect(self.screen, (255, 255, 255), 
                               (bar_x, bar_y, bar_width, bar_height), 1)
                
                # Draw -1, 0, 1 markers (just lines, no labels)
                for marker_pos in [-1, 0, 1]:
                    marker_x = bar_x + bar_width // 2 + int(marker_pos * (bar_width // 2))
                    marker_y = bar_y - 3
                    pygame.draw.line(self.screen, (200, 200, 200), 
                                   (marker_x, marker_y), 
                                   (marker_x, marker_y + bar_height + 6), 1)
            
            # For position and distance inputs (0, 2, 5), draw normal bars
            elif i in [0, 2, 5]:
                bar_x = panel_x + 10
                bar_y = panel_y + y_offset + 18
                
                # Background bar
                pygame.draw.rect(self.screen, (100, 100, 100), 
                               (bar_x, bar_y, bar_width, bar_height))
                
                # Value bar (clamped to [0, 1])
                clamped_value = max(0, min(1, value))
                fill_width = int(clamped_value * bar_width)
                
                # Color based on input type
                if i == 0:  # Bird position
                    color = (100, 200, 255)  # Blue
                else:  # Distances
                    color = (100, 255, 100)  # Green
                
                pygame.draw.rect(self.screen, color, 
                               (bar_x, bar_y, fill_width, bar_height))
                
                # Draw border
                pygame.draw.rect(self.screen, (255, 255, 255), 
                               (bar_x, bar_y, bar_width, bar_height), 1)
                
                # Draw 0, 0.5, 1 markers (just lines, no labels)
                for marker in [0, 0.5, 1]:
                    marker_x = bar_x + int(marker * bar_width)
                    marker_y = bar_y - 3
                    pygame.draw.line(self.screen, (200, 200, 200), 
                                   (marker_x, marker_y), 
                                   (marker_x, marker_y + bar_height + 6), 1)
            
            # For gap top/bottom (3, 4, 6, 7), just show text (no bar)
            elif i in [3, 4, 6, 7]:
                # No bar for these, just text
                pass
            
            y_offset += 35 if i in [0, 1, 2, 5] else 25  # Less spacing for text-only inputs

    def draw(self):
        if not self.render:
            return
        
        BLACK = (0,0,0)
        PIPE_GREEN = (119, 221, 119)
        BIRD_YELLOW = (255, 238, 140)
        BACKGROUND_BLUE = (162, 191, 254)
        OUTLINE_WIDTH = 1

        self.screen.fill(BACKGROUND_BLUE)

        # bird
        pygame.draw.circle(self.screen, BIRD_YELLOW,
                           (int(self.bird.x), int(self.bird.y)), self.bird.radius)
        pygame.draw.circle(self.screen, BLACK,
                           (int(self.bird.x), int(self.bird.y)), self.bird.radius, OUTLINE_WIDTH)

        # pipes
        for pipe in self.pipes:
            gap_top = pipe.gap_y - PIPE_GAP // 2
            gap_bottom = pipe.gap_y + PIPE_GAP // 2

            pygame.draw.rect(self.screen, PIPE_GREEN,
                            (pipe.x, 0, 50, gap_top))
            pygame.draw.rect(self.screen, BLACK,
                            (pipe.x, 0, 50, gap_top), OUTLINE_WIDTH)
            pygame.draw.rect(self.screen, PIPE_GREEN,
                            (pipe.x, gap_bottom, 50, HEIGHT))
            pygame.draw.rect(self.screen, BLACK,
                            (pipe.x, gap_bottom, 50, HEIGHT), OUTLINE_WIDTH)

        font = pygame.font.SysFont('Arial', 30)

        score_surface = font.render(f'Score : {self.bird.score}', True, BLACK)
        score_rect = score_surface.get_rect()
        score_rect.midleft = (20, 20)
        self.screen.blit(score_surface, score_rect)

        if DEBUG_SCORE:
            self.draw_debug()

        self.screen.blit(score_surface, score_rect)

        pygame.display.flip()

    def run_genome(self, net, render=False):
        self.reset()
        alive = True

        while alive:
            inputs = self.get_state()
            output = net.activate(inputs)
            action = 1 if output[0] > 0 else 0

            _, done = self.step(action)
            alive = not done

            self.fitness += 0.01

            if render:
                self.clock.tick(60)
                self.draw()

        return self.fitness

space_was_down = False

if __name__ == "__main__":
    game = FlappyGame(render=True)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        space_down = keys[pygame.K_SPACE]

        action = 1 if space_down and not space_was_down else 0
        space_was_down = space_down

        _, done = game.step(action)
        game.draw()

        if done:
            game.reset()

    pygame.quit()

# end of game

import pygame
import random

#cstes

WIDTH, HEIGHT = 600,600
GRAVITY = 0.45
FLAP_STRENGTH = -7
PIPE_SPEED = -3
PIPE_DISTANCE = 200
PIPE_GAP = 150
MAX_VELOCITY = 13

print();print()
DEBUG_SCORE = str(input('show debug? (y/n): ')) in ['yes', 'y']

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

        if self.y <= 0 or self.y >= HEIGHT:
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
    def __init__(self, render=True):
        self.render = render

        if render:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT)) if render else None
            self.clock = pygame.time.Clock()
        else:
            self.screen = None
            self.clock = None
        self.reset()

    def reset(self):
        self.bird = Bird()
        self.pipes = [Pipe(WIDTH + 100)]
        self.frame = 0
        self.fitness = 0
        return self.get_state()
    
    def get_state(self):
        pipe1 = self.pipes[0]
        pipe2 = self.pipes[1] if len(self.pipes) > 1 else pipe1

        return [ # normalized inputs for neat 
            self.bird.y / HEIGHT,                  # relative height
            self.bird.vel / MAX_VELOCITY,          # relative velocity
            (pipe1.x - self.bird.x) / WIDTH,       # first pipe distance
            (pipe1.gap_y - PIPE_GAP//2) / HEIGHT,  # first pipe gap top
            (pipe1.gap_y + PIPE_GAP//2) / HEIGHT,  # first pipe gap bot
            (pipe2.x - self.bird.x) / WIDTH,       # next pipe distance
            (pipe2.gap_y - PIPE_GAP//2) / HEIGHT,  # next pipe gap top
            (pipe2.gap_y + PIPE_GAP//2) / HEIGHT,  # next pipe gap bot
        ]
    
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

        # cull vieux pipes
        if self.pipes[0].x < -50:
            self.pipes.pop(0)

        # score 
        if not self.pipes[0].passed and self.bird.x > self.pipes[0].x + 25:
            self.bird.score += 1
            self.pipes[0].passed = True

        self.frame += 1

        done = not self.bird.alive
        return self.get_state(), done

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

        if DEBUG_SCORE:
            fitness_surface = font.render(f'Fitness : {self.fitness:.2f}', True, BLACK)
            fitness_rect = fitness_surface.get_rect()
            fitness_rect.midright = (WIDTH - 20, HEIGHT - 20)

        self.screen.blit(score_surface, score_rect)
        self.screen.blit(fitness_surface, fitness_rect)

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

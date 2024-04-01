import pygame
import os
import random
import neat

ai_playing = True
generation = 0
PRINT_LINES = True

# TAMANHO DA TELA
WIDTH_SCREEN = 550
HEIGHT_SCREEN = 800

# IMAGENS
IMAGE_PIPE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGE_DOUBLE_PIPE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'doublepipe.png')))
IMAGE_GROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGE_BG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGE_BIRD = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
]

# FONTE
pygame.font.init()
POINTS_FONT = pygame.font.SysFont('arial', 50)


class Bird:
    IMGS = IMAGE_BIRD
    MAX_ROTATION = 25
    ROTATION_SPEED = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.img_count = 0
        self.image = self.IMGS[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y

    def move(self):
        self.time += 1
        movement = 1.5 * (self.time ** 2) + self.speed * self.time

        if movement > 16:
            movement = 16
        elif movement < 0:
            movement -= 2

        self.y += movement

        if movement < 0 or self.y < (self.height + 50):
            if self.angle < self.MAX_ROTATION:
                self.angle = self.MAX_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.ROTATION_SPEED

    def draw(self, screen):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.image = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.image = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.image = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.image = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 4 + 1:
            self.image = self.IMGS[0]
            self.img_count = 0

        if self.angle <= 80:
            self.image = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_img = pygame.transform.rotate(self.image, self.angle)
        pos_center = self.image.get_rect(topleft=(self.x, self.y)).center
        rectangle = rotated_img.get_rect(center=pos_center)
        screen.blit(rotated_img, rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    DISTANCE = 200
    SPEED = 5  # Velocidade de movimento dos canos

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top_pos = 0
        self.bot_pos = 0
        self.TOP_PIPE = pygame.transform.flip(IMAGE_PIPE, False, True)
        self.BOT_PIPE = IMAGE_PIPE
        self.Pass = False
        self.define_height()
        self.top_bottom_left = self.bot_pos - self.DISTANCE
        self.VEL_VERTICAL = random.choice([1, 2])

    def define_height(self):
        self.height = random.randrange(50, 450)
        self.top_pos = self.height - self.TOP_PIPE.get_height()
        self.bot_pos = self.height + self.DISTANCE

    def move(self):
        self.x -= self.SPEED  # Movimento para a esquerda
        self.height += self.VEL_VERTICAL * 2
        if self.height < 50:
            self.height = 50
            self.VEL_VERTICAL *= -1
        elif self.height > 450:
            self.height = 450
            self.VEL_VERTICAL *= -1
        self.top_pos = self.height - self.TOP_PIPE.get_height()
        self.bot_pos = self.height + self.DISTANCE

    def draw(self, screen):
        screen.blit(self.TOP_PIPE, (self.x, self.top_pos))
        screen.blit(self.BOT_PIPE, (self.x, self.bot_pos))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TOP_PIPE)
        bot_mask = pygame.mask.from_surface(self.BOT_PIPE)

        top_dist = (self.x - bird.x, self.top_pos - round(bird.y))
        bot_dist = (self.x - bird.x, self.bot_pos - round(bird.y))

        bot_point = bird_mask.overlap(bot_mask, bot_dist)
        top_point = bird_mask.overlap(top_mask, top_dist)

        if bot_point or top_point:
            return True
        else:
            return False


class DoublePipe:
    DISTANCE = 200
    SPEED = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top_pos = 0
        self.bot_pos = 0
        self.TOP_PIPE = pygame.transform.flip(IMAGE_DOUBLE_PIPE, False, True)
        self.BOT_PIPE = IMAGE_DOUBLE_PIPE
        self.Pass = False
        self.define_height()
        self.top_bottom_left = self.bot_pos - self.DISTANCE
        self.VEL_VERTICAL = random.choice([1, 2.5])

    def define_height(self):
        self.height = random.randrange(50, 450)
        self.top_pos = self.height - self.TOP_PIPE.get_height()
        self.bot_pos = self.height + self.DISTANCE

    def move(self):
        self.x -= self.SPEED
        self.height += self.VEL_VERTICAL * 1
        if self.height < 50:
            self.height = 50
            self.VEL_VERTICAL *= -1
        elif self.height > 450:
            self.height = 450
            self.VEL_VERTICAL *= -1
        self.top_pos = self.height - self.TOP_PIPE.get_height()
        self.bot_pos = self.height + self.DISTANCE

    def draw(self, screen):
        screen.blit(self.TOP_PIPE, (self.x, self.top_pos))
        screen.blit(self.BOT_PIPE, (self.x, self.bot_pos))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TOP_PIPE)
        bot_mask = pygame.mask.from_surface(self.BOT_PIPE)

        top_dist = (self.x - bird.x, self.top_pos - round(bird.y))
        bot_dist = (self.x - bird.x, self.bot_pos - round(bird.y))

        bot_point = bird_mask.overlap(bot_mask, bot_dist)
        top_point = bird_mask.overlap(top_mask, top_dist)

        if bot_point or top_point:
            return True
        else:
            return False


class Ground:
    SPEED = 5
    WIDTH = IMAGE_GROUND.get_width()
    IMAGE = IMAGE_GROUND

    def __init__(self, y):
        self.y = y
        self.x0 = 0
        self.x1 = self.WIDTH

    def move(self):
        self.x0 -= self.SPEED
        self.x1 -= self.SPEED

        if self.x0 + self.WIDTH < 0:
            self.x0 = self.x1 + self.WIDTH
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x0 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMAGE, (self.x0, self.y))
        screen.blit(self.IMAGE, (self.x1, self.y))


def draw_screen(screen, birds, pipes, ground, points):
    screen.blit(IMAGE_BG, (0, 0))
    for bird in birds:
        bird.draw(screen)
    for pipe in pipes:
        pipe.draw(screen)

    text = POINTS_FONT.render(f"Pontuação: {points}", 1, (255, 255, 255))
    screen.blit(text, (WIDTH_SCREEN - 10 - text.get_width(), 10))

    if ai_playing:
        text = POINTS_FONT.render(f"Geracao: {generation}", 1, (255, 255, 255))
        screen.blit(text, (10, 10))
        text = POINTS_FONT.render(f"Individuos: {len(birds)}", 1, (255, 255, 255))
        screen.blit(text, (10, 60))

        if PRINT_LINES:
            if len(birds) > 0:
                for pipe in pipes:
                    pygame.draw.line(screen, (255, 0, 0), (pipe.x, pipe.bot_pos), (birds[0].x, birds[0].y), 2)
                    pygame.draw.line(screen, (255, 0, 0), (pipe.x, pipe.top_bottom_left), (birds[0].x, birds[0].y), 2)

    ground.draw(screen)
    pygame.display.update()


def main(dnas, config):
    global generation
    generation += 1

    if ai_playing:
        networks = []
        dna_list = []
        birds = []
        for _, dna in dnas:
            network = neat.nn.FeedForwardNetwork.create(dna, config)
            networks.append(network)
            dna.fitness = 0
            dna_list.append(dna)
            birds.append(Bird(230, 350))
    else:
        birds = [Bird(230, 350)]

    ground = Ground(730)
    pipes = [Pipe(700)]
    last_double = False
    screen = pygame.display.set_mode((WIDTH_SCREEN, HEIGHT_SCREEN))
    points = 0
    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
            if not ai_playing:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        for bird in birds:
                            bird.jump()

        i_pipe = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > (pipes[0].x + pipes[0].TOP_PIPE.get_width()):
                i_pipe = 1
        else:
            running = False
            break

        for i, bird in enumerate(birds):
            bird.move()
            if ai_playing:
                dna_list[i].fitness += 0.1
                output = networks[i].activate((bird.y,
                                               abs(bird.y - pipes[i_pipe].top_bottom_left),
                                               abs(bird.y - pipes[i_pipe].bot_pos)))
                if output[0] > 0.5:
                    bird.jump()
        ground.move()

        for pipe in pipes:
            pipe.move()

        addPipe = False
        remove_pipe = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)
                    if ai_playing:
                        dna_list[i].fitness -= 1
                        dna_list.pop(i)
                        networks.pop(i)
                if not pipe.Pass and bird.x > pipe.x:
                    pipe.Pass = True
                    addPipe = True
            pipe.move()
            if pipe.x + pipe.TOP_PIPE.get_width() < 0:
                remove_pipe.append(pipe)

        if addPipe:
            lottery = int(random.randrange(1,4))

            if lottery == 3:
                pipes.append(DoublePipe(650))
                points += 1
                last_double = True
            else:
                points += 1
                if last_double:
                    pipes.append(Pipe(700))
                else:
                    pipes.append(Pipe(random.randrange(550, 700)))
                last_double = False

            if ai_playing:
                for dna in dna_list:
                    dna.fitness += 2
        for pipe in remove_pipe:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y + bird.image.get_height()) > ground.y or bird.y < 0:
                birds.pop(i)
                if ai_playing:
                    dna_list[i].fitness -= 1
                    dna_list.pop(i)
                    networks.pop(i)

        if not ai_playing:
            if len(birds) < 1:
                running = False
                pygame.quit()
                print("Fim de Jogo!")
                print(f"Pontuação: {points}")
                quit()

        draw_screen(screen, birds, pipes, ground, points)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    if ai_playing:
        population.run(main)
    else:
        main(None, None)


if __name__ == '__main__':
    config_path = 'config.txt'
    run(config_path)


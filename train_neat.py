import neat
from flappy_game import FlappyGame

MAX_GENERATIONS = int(input('max generations? (~150 recommended):'))
RENDER_EACH_GEN = str(input('render each generation? (y/n): ')) in ['yes', 'y']


def eval_genomes(genomes, config):
    game = FlappyGame(render=RENDER_EACH_GEN)

    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        fitness = game.run_genome(net, render=RENDER_EACH_GEN)
        genome.fitness = fitness

def run():
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        "flappy-config"
    )

    pop = neat.Population(config)

    # reporters
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    for gen in range(MAX_GENERATIONS):
        winner = pop.run(eval_genomes, 1)

        print(f"Best fitness: {winner.fitness:.2f}")

    game = FlappyGame(render=True)
    net = neat.nn.FeedForwardNetwork.create(winner, config)
    game.run_genome(net, render=True)


if __name__ == "__main__":
    run()

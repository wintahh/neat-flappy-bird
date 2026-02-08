import neat
import pickle
import os
from joblib import Parallel, delayed
from flappy_game import FlappyGame

MAX_GENERATIONS = int(input('max generations? (~150 recommended): '))
DEBUG_SCORE = str(input('show debug? (y/n): ')).lower() in ['yes', 'y']

import sys
sys.modules['flappy_game'].DEBUG_SCORE = DEBUG_SCORE

def eval_genomes_parallel(genomes, config):
    genome_list = [(genome, config) for _, genome in genomes]
    
    num_cores = -1  # use all available cores
    results = Parallel(n_jobs=num_cores)(delayed(eval_genome)(gc) for gc in genome_list)
    
    for i, (genome_id, genome) in enumerate(genomes):
        genome.fitness = results[i]

def eval_genomes_serial(genomes, config):
    for genome_id, genome in genomes:
        game = FlappyGame(render=False)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        fitness = game.run_genome(net, render=False)
        genome.fitness = fitness

def run():
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         "flappy-config")
    
    pop = neat.Population(config)
    
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    
    try:
        # try to parallel
        print("Attempting parallel evaluation with joblib...")
        winner = pop.run(eval_genomes_parallel, MAX_GENERATIONS)
    except Exception as e:
        print(f"Parallel evaluation failed: {e}")
        print("Falling back to serial evaluation...")
        winner = pop.run(eval_genomes_serial, MAX_GENERATIONS)
    
    print(f"\nBest fitness: {winner.fitness:.2f}")
    
    with open('best_genome.pkl', 'wb') as f:
        pickle.dump(winner, f)
    
    print("\nShowing best genome...")
    
    game = FlappyGame(render=True)
    net = neat.nn.FeedForwardNetwork.create(winner, config)
    game.run_genome(net, render=True)

if __name__ == "__main__":
    run()
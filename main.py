import time

from scripts.NEAT.functions import random_float

from scripts.NEAT import *
from scripts.flappybird import FlappyBirdGame, GenomeBird


if __name__ == "__main__":
    game = FlappyBirdGame(False)

    for i in range(4):
        genome = Genome(nodes=[
            NodeGene(NodeType.Input, OperatorType.Plus, io_index=0),
            NodeGene(NodeType.Input, OperatorType.Plus, io_index=1),
            NodeGene(NodeType.Input, OperatorType.Plus, io_index=2),
            NodeGene(NodeType.Hidden, OperatorType.Plus),
            NodeGene(NodeType.Output, OperatorType.Plus),
        ], connections=[
            ConnectionGene(0, 3, random_float(-10, 10), OperatorType.Multiply),
            ConnectionGene(1, 3, random_float(-10, 10), OperatorType.Multiply),
            ConnectionGene(2, 3, random_float(-10, 10), OperatorType.Multiply),
            ConnectionGene(3, 4, random_float(-10, 10), OperatorType.Plus),
        ])

        bird = GenomeBird(genome, 20, (80, 250))
        game.birds.append(bird)

    game.run_without_pygame()

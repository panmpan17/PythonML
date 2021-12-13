import random
import time
import json
import argparse
from typing import List


from scripts.NEAT import *
from scripts.flappybird import FlappyBirdGame, GenomeBird, Bird
from scripts.navigation_2d import GenomeCharacter, NavigationGame, Character


class TerminalController:
    def __init__(self) -> None:
        self.game: FlappyBirdGame = None

        self.mode = ""
        self.gaps = []
        self.run_pygame = False
        self.tick_limit = False

    def parse_enviroment_argument(self):
        parser = argparse.ArgumentParser()

        # Training engine configuration
        parser.add_argument("mode", choices=["player", "empty", "last"])
        parser.add_argument("--demo", action="store_true",
                            help="Wether turn on pygame and tick limit",
                            default=False)

        # Flappy game trainning parameter
        parser.add_argument("--gap", action="append",
                            type=int,
                            help="Gap between up and bottom grounds",
                            default=[])
        parser.add_argument("--gap-repeat", type=int, default=6)

        args = parser.parse_args()

        self.mode = args.mode
        if args.mode == "player":
            args.demo = True

        self.run_pygame = args.demo
        self.tick_limit = args.demo

        if args.gap == []:
            args.gap = [80, 70, 60, 55, 50]

        for gap in args.gap:
            for i in range(args.gap_repeat):
                self.gaps.append(gap)

    def setup(self):
        self.setup_game()

        if self.mode == "player":
            self.setup_player()
        elif self.mode == "empty":
            self.setup_empty_bird()
        else:
            self.setup_from_last_training()

    def setup_game(self):
        self.game = FlappyBirdGame(
            self.run_pygame,
            gaps=self.gaps,
            tick_limit=self.tick_limit)

    def setup_player(self):
        bird = Bird(20, (40, 250))
        self.game.birds.append(bird)

    def setup_from_last_training(self):
        with open("result.json") as f:
            genome = Genome.fromJSON(json.load(f))

            bird = GenomeBird(genome, 20, (40, 250))
            self.game.birds.append(bird)

    def setup_empty_bird(self):
        base_genome = Genome(nodes=[
            NodeGene(NodeType.Input, OperatorType.Plus, io_index=0),
            NodeGene(NodeType.Input, OperatorType.Plus, io_index=1),
            NodeGene(NodeType.Input, OperatorType.Plus, io_index=2),
            NodeGene(NodeType.Output, OperatorType.Plus),
            NodeGene(NodeType.Output, OperatorType.Plus),
        ], connections=[])

        mutations = connection_mutations(base_genome, 0, 0)

        for mutation in mutations:
            variants = connection_weight_random_add(mutation, 20, -4, 4)
            for variant in variants:
                bird = GenomeBird(variant, 20, (40, 250))
                self.game.birds.append(bird)

    def run(self):
        self.game.execute()


class Navgation2DTerminalController:
    def __init__(self):
        self.game = NavigationGame(False, tick_limit=False)

    def setup(self):
        self.setup_empty_genome()

    def setup_from_read(self):
        with open("result/character-keyboard.json") as f:
            genomes = json.load(f)

            # for genome_json in genomes:
            genome_json = genomes[0]
            genome = Genome.fromJSON(genome_json)

            character = GenomeCharacter(genome, (50, 100), 10)
            self.game.add_character(character=character)

    def setup_empty_genome(self):
        nodes: List[NodeGene] = []
        for i in range(16):
            nodes.append(NodeGene(NodeType.Input, OperatorType.Plus, io_index=i))
        
        nodes.append(NodeGene(NodeType.Output, OperatorType.Plus))
        nodes.append(NodeGene(NodeType.Output, OperatorType.Plus))
        nodes.append(NodeGene(NodeType.Output, OperatorType.Plus))

        base_genome = Genome(nodes=nodes, connections=[])

        mutations = random.choices(connection_mutations(base_genome, 0, 0), k=20)

        for mutation in mutations:
            variants = connection_weight_random_add(mutation, 10, -4, 4)
            for variant in variants:
                character = GenomeCharacter(variant, (50, 100), 10)
                self.game.add_character(character=character)

    def run(self):
        try:
            self.game.start()
        except KeyboardInterrupt:
            self.game.save_characters_unexpected_quit(20, "keyboard")


if __name__ == "__main__":
    # controller = TerminalController()
    # controller.parse_enviroment_argument()
    # controller.setup()
    # controller.run()

    controller = Navgation2DTerminalController()
    controller.setup()
    controller.run()

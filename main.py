from scripts.NEAT import *
import pprint


if __name__ == "__main__":
    # genome = Genome(nodes=[
    #     NodeGene(NodeType.Input, OperatorType.Plus, io_index=0),
    #     NodeGene(NodeType.Input, OperatorType.Plus, io_index=1),
    #     # NodeGene(NodeType.Hidden, OperatorType.Plus),
    #     NodeGene(NodeType.Output, OperatorType.Plus),
    # ], connections=[])

    # new_pairs = analyze_potential_new_connections(genome=genome)
    # print(new_pairs)

    # genome = Genome(nodes=[
    #     NodeGene(NodeType.Input, OperatorType.Plus, io_index=0),
    #     NodeGene(NodeType.Input, OperatorType.Plus, io_index=1),
    #     # NodeGene(NodeType.Hidden, OperatorType.Plus),
    #     NodeGene(NodeType.Output, OperatorType.Plus),
    # ], connections=[
    #     ConnectionGene(0, 2, 1, OperatorType.Plus)
    # ])

    # new_pairs = analyze_potential_new_connections(genome=genome)
    # print(new_pairs)

    genome = Genome(nodes=[
        NodeGene(NodeType.Input, OperatorType.Plus, io_index=0),
        NodeGene(NodeType.Input, OperatorType.Plus, io_index=1),
        # NodeGene(NodeType.Hidden, OperatorType.Plus),
        NodeGene(NodeType.Output, OperatorType.Plus),
    ], connections=[])

    mutations = connection_mutations(genome=genome, weight_min=-4, weight_max=4)
    pprint.pprint(genome)
    for mutation in mutations:
        pprint.pprint(mutation)

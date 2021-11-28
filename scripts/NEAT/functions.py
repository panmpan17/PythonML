import random
import copy

from scripts import NEAT
from typing import List
from .structure import ConnectionGene, Genome, NodeGene, NodeType, OperatorType, ConnectionPair


def random_float(min_:float, max_:float) -> float:
    return random.random() * (max_ - min_) + min_


def genome_feed_data(genome:Genome, inputs:List[float]) -> List[float]:
    values = []

    for node in genome.nodes:
        if node.type == NodeType.Input:
            values.append(inputs[node.io_index])
        else:
            values.append(0)

    for connection in genome.connections:
        if connection.enabled:
            if connection.weight_operator == OperatorType.Plus:
                value = values[connection.input_index] + connection.weight
            elif connection.weight_operator == OperatorType.Multiple:
                value = values[connection.input_index] * connection.weight
            
            output_node_operator = genome.nodes[connection.output_index].add_on_operator
            if output_node_operator == OperatorType.Plus:
                values[connection.output_index] += value
            elif output_node_operator == OperatorType.Multiple:
                if (values[connection.output_index] == 0):
                    values[connection.output_index] = value
                else:
                    values[connection.output_index] *= value

    output_values = []

    for i, node in enumerate(genome.nodes):
        if node.type == NodeType.Output:
            output_values.append(values[i])
    
    return output_values


def get_exist_pair_in_genome(genome:Genome) -> List[ConnectionPair]:
    existed_pairs = []

    for connection in genome.connections:
        existed_pairs.append(ConnectionPair(connection.input_index, connection.output_index))
    
    return existed_pairs


def analyze_potential_new_connections(genome:Genome) -> List[ConnectionPair]:
    input_node_index = []
    output_node_index = []

    # Analyze genome potential connection
    for i, node in enumerate(genome.nodes):
        if node.type == NodeType.Input:
            input_node_index.append(i)
        elif node.type == NodeType.Hidden:
            input_node_index.append(i)
            output_node_index.append(i)
        elif node.type == NodeType.Output:
            output_node_index.append(i)

    pairs = []
    existed_pairs = get_exist_pair_in_genome(genome=genome)

    for input_index in input_node_index:
        for output_index in output_node_index:
            if input_index != output_index:
                new_pair = ConnectionPair(input_node_index=input_index,
                                          output_nodex_index=output_index)
                
                if new_pair not in existed_pairs and new_pair not in pairs:
                    pairs.append(new_pair)

    return pairs


def mutate_genome_by_add_new_connection(genome:Genome,
                                        connection:ConnectionGene) -> Genome:
    genome_copy = copy.deepcopy(genome)
    genome_copy.connections.append(connection)

    return genome_copy


def connection_mutations(genome:Genome, weight_min:float,
                         weight_max:float) -> List[Genome]:
    new_connection_pairs = analyze_potential_new_connections(genome=genome)
    mutations = []

    for pair in new_connection_pairs:
        weight = random_float(weight_min, weight_max)
        # pair.input_node_index
        connection = ConnectionGene(pair.input_node_index,
                                    pair.output_nodex_index,
                                    weight, OperatorType.Plus)

        mutations.append(mutate_genome_by_add_new_connection(
            genome=genome, connection=connection))

        connection = ConnectionGene(pair.input_node_index,
                                    pair.output_nodex_index,
                                    weight, OperatorType.Multiple)

        mutations.append(mutate_genome_by_add_new_connection(
            genome=genome, connection=connection))

    return mutations

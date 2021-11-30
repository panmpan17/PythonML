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
            elif connection.weight_operator == OperatorType.Multiply:
                value = values[connection.input_index] * connection.weight
            
            output_node_operator = genome.nodes[connection.output_index].add_on_operator
            if output_node_operator == OperatorType.Plus:
                values[connection.output_index] += value
            elif output_node_operator == OperatorType.Multiply:
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
                                    weight, OperatorType.Multiply)

        mutations.append(mutate_genome_by_add_new_connection(
            genome=genome, connection=connection))

    return mutations


def mutate_genome_by_insert_connection(
        genome:Genome, connection_index:int, new_node:NodeGene,
        connection_1:ConnectionGene, connection_2:ConnectionGene) -> Genome:
    genome_copy = copy.deepcopy(genome)
    genome_copy.connections[connection_index].enabled = False

    genome_copy.nodes.append(new_node)
    genome_copy.connections.append(connection_1)
    genome_copy.connections.append(connection_2)

    return genome_copy


def insert_node_mutations(genome:Genome) -> List[Genome]:
    mutations = []
    for i, connection in enumerate(genome.connections):
        middle_index = len(genome.nodes)

        new_node = NodeGene(NodeType.Hidden, OperatorType.Plus)
        first_half = ConnectionGene(
            connection.input_index, middle_index, 1,
            OperatorType.Multiply)
        second_half = ConnectionGene(
            middle_index, connection.output_index,
            connection.weight, connection.weight_operator)

        mutations.append(mutate_genome_by_insert_connection(genome, i, new_node, first_half, second_half))

        first_half = ConnectionGene(
            connection.input_index, middle_index, 0,
            OperatorType.Plus)

        mutations.append(mutate_genome_by_insert_connection(genome, i, new_node, first_half, second_half))

    return mutations


def connection_weight_random_add(genome:Genome, count:int, range_min:float, range_max:float) -> List[Genome]:
    variants = []

    for i in range(count):
        variant:Genome = copy.deepcopy(genome)
        for connection in variant.connections:
            connection.weight += random_float(range_min, range_max)
        variants.append(variant)
    
    return variants

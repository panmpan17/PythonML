from scripts import NEAT
from typing import List
from .structure import Genome, NodeGene, NodeType, OperatorType, ConnectionPair


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


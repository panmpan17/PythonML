from dataclasses import dataclass
from enum import Enum
from typing import List


class NodeType(Enum):
    Input = 0
    Output = 1
    Hidden = 2


class OperatorType(Enum):
    Plus = 0
    Multiple = 1


class NodeGene:
    # uuid: str
    # type: NodeType
    # io_index: int
    # value: float
    # add_on_operator: OperatorType

    def __init__(self, type:NodeType, add_on_operator:OperatorType,
                 uuid:str=None, io_index:int=0) -> None:
        self.uuid = uuid
        self.type = type
        self.io_index = io_index
        self.add_on_operator = add_on_operator


class ConnectionGene:
    # uuid: str
    # input_index: int
    # output_index: int
    # weight: float
    # weight_operator: OperatorType
    # enabled: bool

    def __init__(self, input_index:int, output_index:int, weight:float,
                 weight_operator:OperatorType, uuid:str=None,
                 enabled:bool=True) -> None:
        self.uuid = uuid
        self.input_index = input_index
        self.output_index = output_index
        self.weight = weight
        self.weight_operator = weight_operator
        self.enabled = enabled

@dataclass
class Genome:
    nodes: List[NodeGene]
    connections: List[ConnectionGene]


@dataclass
class ConnectionPair:
    input_node_index: int
    output_nodex_index: int

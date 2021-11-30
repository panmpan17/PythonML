import json

from dataclasses import dataclass
from enum import Enum
from os import stat
from typing import List
from uuid import uuid1


class NodeType(Enum):
    Input = 0
    Output = 1
    Hidden = 2


class OperatorType(Enum):
    Plus = 0
    Multiply = 1


@dataclass(init=False)
class NodeGene:
    uuid: str
    type: NodeType
    io_index: int
    add_on_operator: OperatorType

    def __init__(self, type:NodeType, add_on_operator:OperatorType,
                 uuid:str=None, io_index:int=0) -> None:
        if uuid is None:
            self.uuid = str(uuid1())
        else:
            self.uuid = uuid

        self.type = type
        self.io_index = io_index
        self.add_on_operator = add_on_operator

    def toJSON(self):
        return {
            "uuid": self.uuid,
            "type": self.type.value,
            "io_index": self.io_index,
            "add_on_operator": self.add_on_operator.value,
        }

    @staticmethod
    def fromJSON(json):
        return NodeGene(
            type=NodeType(json["type"]),
            uuid=json["uuid"],
            io_index=json["io_index"],
            add_on_operator=OperatorType(json["add_on_operator"]))


@dataclass(init=False)
class ConnectionGene:
    uuid: str
    input_index: int
    output_index: int
    weight: float
    weight_operator: OperatorType
    enabled: bool

    def __init__(self, input_index:int, output_index:int, weight:float,
                 weight_operator:OperatorType, uuid:str=None,
                 enabled:bool=True) -> None:
        if uuid is None:
            self.uuid = str(uuid1())
        else:
            self.uuid = uuid

        self.input_index = input_index
        self.output_index = output_index
        self.weight = weight
        self.weight_operator = weight_operator
        self.enabled = enabled

    def toJSON(self):
        return {
            "uuid": self.uuid,
            "input_index": self.input_index,
            "output_index": self.output_index,
            "weight": self.weight,
            "weight_operator": self.weight_operator.value,
            "enabled": self.enabled,
        }

    @staticmethod
    def fromJSON(json):
        return ConnectionGene(
            uuid=json["uuid"],
            input_index=json["input_index"],
            output_index=json["output_index"],
            weight=json["weight"],
            weight_operator=OperatorType(json["weight_operator"]),
            enabled=json["enabled"])


@dataclass
class Genome:
    nodes: List[NodeGene]
    connections: List[ConnectionGene]

    def toJSON(self):
        return {
            "nodes": self.nodes,# json.dumps(self.nodes, default=lambda obj: obj.toJSON()),
            "connections": self.connections,# json.dumps(self.connections, default=lambda obj: obj.toJSON()),
        }

    @staticmethod
    def fromJSON(json):
        if "nodes" not in json or not isinstance(json["nodes"], list):
            raise ValueError
        if "connections" not in json or not isinstance(json["connections"], list):
            raise ValueError

        return Genome(
            nodes=[NodeGene.fromJSON(node) for node in json["nodes"]],
            connections=[ConnectionGene.fromJSON(conn) for conn in json["connections"]])
    
    # def __eq__(self, o: object) -> bool:
    #     if isinstance(o, Genome):
    #         if len(o.nodes) == len(self.nodes):
    #             for i, node in enumerate(o.nodes):
    #                 if node != self.nodes[i]:
    #                     print(self.nodes[i], node)
    #                     print(127)
    #                     return False
    #         else:
    #             return False

    #         if len(o.connections) == len(self.connections):
    #             for i, connection in enumerate(o.connections):
    #                 if connection != self.connections[i]:
    #                     print(135)
    #                     return False
    #         else:
    #             return False

    #         return True
    #     else:
    #         return False


@dataclass
class ConnectionPair:
    input_node_index: int
    output_nodex_index: int


@dataclass
class Range:
    min_:float
    max_:float

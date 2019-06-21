"""
This module defines the Edge dataclass as well as two functions to read and
write an Edge object to/from string, respectively
"""
from dataclasses import dataclass
import re

_guid_pattern = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$')


@dataclass
class Link:
    """
    Class to represent a link between two datasets. The link is a little graph
    with two nodes (head and tail) and a directed edge.

    Attributes:
        head: a guid representing the head of the graph
        tail: a guid representing the tail of the graph
        edge_type: a name to represent the type of the edge
        description: free-form optional field add a description of the graph
    """
    head: str
    tail: str
    edge_type: str
    description: str = ""

    def validate_node(self, node_guid: str, node: str) -> None:
        """
        Validate that the guid given is a valid guid.

        Args:
            node_guid: the guid
            node: either "head" or "tail"
        """
        if _guid_pattern.match(node_guid):
            return
        else:
            raise ValueError(
                f'The guid given for {node} is not a valid guid. Received '
                f'{node_guid}.')

    def __post_init__(self):
        self.validate_node(self.head, "head")
        self.validate_node(self.tail, "tail")

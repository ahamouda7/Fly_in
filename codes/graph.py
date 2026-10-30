
"""Build a graph of zones, movement costs, and connections."""

from typing import Any
from parser import Parser


class Zone:
    """Represent a zone with its movement cost and neighboring zones."""

    def __init__(self, name: str, zone_type: str) -> None:
        """Initialize the zone's name and type."""
        self.name = name
        self.zone_type = zone_type

    def movement_cost(self) -> int:
        """Return the movement cost based on the zone type."""
        if self.zone_type == "normal":
            return 1
        elif self.zone_type == "priority":
            return 1
        elif self.zone_type == "restricted":
            return 2
        else:
            return -1

    def neighbors(self) -> list[str]:
        """Return the names of all zones connected to this zone."""
        neighbors_names = []
        configs = Parser().pars()
        if configs is None:
            raise ValueError("Invalid configuration")
        for link in configs["connections"]:
            if self.name in link["connection"]:
                new_neighbor = (
                    link["connection"][1]
                    if self.name == link["connection"][0]
                    else link["connection"][0]
                )
                neighbors_names.append(new_neighbor)
        return neighbors_names


class Graph:
    """Build a graph containing each zone's cost and neighbors."""

    def __init__(self) -> None:
        """Load and store the map configuration."""
        configs = Parser().pars()
        if configs is None:
            raise ValueError("Invalid configuration")
        self.configs = configs

    def hubs(self) -> list[dict[str, Any]]:
        """Return all hubs, including the start and end hubs."""
        hubs = []
        for hub in self.configs:
            if hub == "start_hub" or hub == "end_hub":
                hubs.append(self.configs[hub])
            elif hub == "hubs":
                for h in self.configs[hub]:
                    hubs.append(h)
        return hubs

    def graph(self) -> dict[str, tuple[int, list[str]]]:
        """Build a dictionary mapping each zone to its cost and neighbors."""
        graph_dict = {}
        start_name = self.configs["start_hub"]["name"]
        for hub in self.hubs():
            hub_graph = Zone(hub["name"], hub["zone"])
            cost = (
                hub_graph.movement_cost()
                if hub_graph.name != start_name
                else 0
                )
            neighbors = hub_graph.neighbors()
            graph_dict[hub_graph.name] = (cost, neighbors)
        return graph_dict

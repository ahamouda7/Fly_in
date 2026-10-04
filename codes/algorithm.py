from math import inf
from graph import Graph
from parser import Parser


class Dijkstra:
    configs = Parser().pars()
    graph_dict = Graph().graph()

    def algo(self, blocked=None):
        if blocked is None:
            blocked = ""

        table = {}
        start_hub_name = self.configs["start_hub"]["name"]
        goal = self.configs["end_hub"]["name"]

        for hub in self.graph_dict:
            table[hub] = (
                [0, None]
                if hub == start_hub_name
                else [inf, None]
                )

        unvisited = [
            hub
            for hub in self.graph_dict
            if hub != blocked
            ]
        current_zone = start_hub_name
        while True:
            neighbors = self.graph_dict[current_zone][1]
            for neighbor in neighbors:
                if neighbor == blocked:
                    continue

                if neighbor not in unvisited:
                    continue

                cost = self.graph_dict[neighbor][0]
                if cost == -1:
                    continue

                new_distance = table[current_zone][0] + cost
                if new_distance < table[neighbor][0]:
                    table[neighbor] = [new_distance, current_zone]

            if current_zone == goal:
                break

            unvisited.remove(current_zone)

            current_zone = min(
                unvisited,
                key=lambda hub: table[hub][0]
            )

        if table[goal][0] == inf:
            return []

        path = []
        zone = goal
        while zone != start_hub_name:
            path.append(zone)
            zone = table[zone][1]

        path.append(start_hub_name)
        path.reverse()

        return path


print(Dijkstra().algo())

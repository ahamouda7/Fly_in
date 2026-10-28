from parser import Parser


class Zone:
    def __init__(self, name, zone_type):
        self.name = name
        self.zone_type = zone_type

    def movement_cost(self):
        if self.zone_type == "normal":
            return 1
        elif self.zone_type == "priority":
            return 1
        elif self.zone_type == "restricted":
            return 2
        else:
            return -1

    def neighbors(self):
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
    def __init__(self):
        configs = Parser().pars()
        if configs is None:
            raise ValueError("Invalid configuration")
        self.configs = configs

    def hubs(self):
        hubs = []
        for hub in self.configs:
            if hub == "start_hub" or hub == "end_hub":
                hubs.append(self.configs[hub])
            elif hub == "hubs":
                for h in self.configs[hub]:
                    hubs.append(h)
        return hubs

    def graph(self):
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

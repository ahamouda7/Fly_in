from algorithm import Dijkstra


class Path2:
    def path_cost(self, path: list[str], dijkstra: Dijkstra) -> int:
        cost = 0

        for hub in path[1:]:
            cost += dijkstra.graph_dict[hub][0]

        return cost

    def second_path(self) -> list[str]:
        dijkstra = Dijkstra()
        shortest_path = dijkstra.algo()
        will_blocked = shortest_path[1:-1]
        paths = []

        for hub in will_blocked:
            path = dijkstra.algo(hub)

            if path and (path not in paths):
                paths.append(path)

        if not paths:
            return []

        second_path = min(
            paths,
            key=lambda path: self.path_cost(path, dijkstra)
        )

        return second_path


# print(Path2().second_path())

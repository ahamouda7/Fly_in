from algorithm import Dijkstra


class Path2:
    def second_path(self):
        dijkstra = Dijkstra()
        shortest_path = dijkstra.algo()
        will_blocked = shortest_path[1:-1]
        paths = []

        for path in will_blocked:
            paths.append(dijkstra.algo(path))
        print(paths)


Path2().second_path()

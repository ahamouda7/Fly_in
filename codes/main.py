"""Entry point for the Fly_in project."""

import sys

from algorithm import Dijkstra
from parser import Parser
from second_path import Path2
from simulation import Simulation
from visualization import Visualizer


class Main:
    @staticmethod
    def main() -> None:
        """Parse the map, find paths, simulate drones, and show the results."""
        if len(sys.argv) != 2:
            print("Usage: python main.py <map.txt>", file=sys.stderr)
            sys.exit(1)

        configs = Parser().pars()
        if configs is None:
            sys.exit(1)

        shortest_path = Dijkstra().algo()
        if not shortest_path:
            print("ERROR: No path from start to end.", file=sys.stderr)
            sys.exit(1)

        second_path = Path2().second_path()
        if not second_path:
            # A map can have only one valid path.
            second_path = shortest_path

        print("Shortest path:", " -> ".join(shortest_path))
        print("Second path:", " -> ".join(second_path))

        simulation = Simulation(shortest_path, second_path)
        output, _drones = simulation.simulation()

        print("\nSimulation:")
        for turn in output:
            print(turn)

        try:
            Visualizer().show_visualization(configs, output)
        except ImportError as error:
            if error.name != "pygame":
                raise
            print("\nPygame is missing. Install it with: pip install pygame",
                  file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    Main().main()

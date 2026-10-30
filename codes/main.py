
"""Run the Fly_in project from map parsing to visualization."""

import sys
from algorithm import Dijkstra
from parser import Parser
from second_path import Path2
from simulation import Simulation
from visualization import Visualizer


class Main:
    """Manage the pathfinding, simulation, and visualization process."""

    @staticmethod
    def main() -> None:
        """Find two paths, compare simulations, and display the best result."""

        configs = Parser().pars()
        if configs is None:
            sys.exit(1)

        shortest_path = Dijkstra().algo()
        if not shortest_path:
            print("ERROR: No path from start to end.", file=sys.stderr)
            sys.exit(1)

        second_path = Path2().second_path()
        if not second_path:
            second_path = shortest_path

        print("\nShortest path:", " -> ".join(shortest_path))
        print("Second path:", " -> ".join(second_path))

        simulation1 = Simulation(shortest_path, second_path)
        output1 = simulation1.simulation()

        simulation2 = Simulation(shortest_path, shortest_path)
        output2 = simulation2.simulation()

        if len(output1) > len(output2):
            output = output2
        else:
            output = output1

        print("\nSimulation:")
        for turn in output:
            print(turn)

        Visualizer().show_visualization(configs, output)


if __name__ == "__main__":
    Main().main()

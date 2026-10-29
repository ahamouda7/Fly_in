*This project has been created as part of the 42 curriculum by ahamouda.*

# Fly-in

## Description

Fly-in is a Python project that simulates drones travelling from a start hub to an end hub through a network of connected zones.

The program reads and validates a map file, builds a graph, searches for two possible routes, simulates each drone's movements turn by turn, and displays the result with Pygame.

The map supports four zone types:
- **Normal:** costs 1 to enter.
- **Priority:** also costs 1 in the current pathfinding implementation.
- **Restricted:** costs 2 to enter and requires an extra connection stage during simulation.
- **Blocked:** cannot be entered by the pathfinding algorithm.

Regular zones have a maximum drone capacity, and connections have a maximum number of drones that may use them in one turn. The start and end hubs are treated as having enough capacity for all drones.

## Instructions

You need Python 3.10 or newer and Pygame.

Install Pygame in your Python environment:

```bash
python -m pip install pygame
```

Run the project by passing the path to a map file:

```bash
python codes/main.py maps/medium/03_priority_puzzle.txt
```

On Windows, you can use `py` instead of `python`:

```bash
py codes/main.py maps/medium/03_priority_puzzle.txt
```

To check your code with the tools used during development:

```bash
flake8 codes/
mypy codes/
```

The program prints the selected paths and simulation turns in the terminal, then opens the Pygame window.

## How It Works

1. **Parser:** Reads the map, checks its required fields, coordinates, zone properties, connections, and capacities, and reports invalid input.
2. **Graph:** Creates the neighboring-zone relationships and assigns a movement cost to each zone.
3. **Dijkstra:** Finds a lowest-cost path from the start to the end, avoiding blocked zones.
4. **Second path:** Tries blocking each intermediate hub in the first path, reruns Dijkstra, and keeps the cheapest alternative found.
5. **Simulation:** Assigns drones alternately to the first and second paths, checks zone and connection capacities, and records each turn. If no second path is found, both groups use the first path.
6. **Visualization:** Reconstructs drone positions from the simulation output and displays the map at the selected turn.

Drones sometimes have to wait for capacity to become available. A drone entering a restricted zone passes through an additional connection stage before arriving at that zone.

## Algorithm Explanation

The main routing algorithm is **Dijkstra's algorithm**, which finds a route with the lowest accumulated movement cost according to the project's graph.

- Normal zones cost **1**.
- Priority zones currently cost **1**, the same as normal zones.
- Restricted zones cost **2**.
- Blocked zones are skipped.
- The algorithm stores the best known distance to each zone and the previous zone on that route.
- It repeatedly chooses the unvisited zone with the smallest distance and updates its neighbors.
- Once the end is reached, the route is reconstructed using the stored previous zones.
- To find another route, `Path2` temporarily excludes each intermediate zone of the first route, one at a time, and compares the resulting paths by cost.

During the simulation, each drone tries to advance one stage per turn. The program checks available space at the destination and how many drones have already used a connection in the current turn. For restricted-zone movements, it accounts for destination space before the drone completes its journey through the connection.

## Visualisation

The project uses **Pygame** to display the simulation on a dark background.

- **Right arrow:** Show the next turn.
- **Left arrow:** Return to the previous turn.
- **R:** Reset to turn 0.
- **Esc** or the window close button: Exit the visualization.

Zones are drawn as colored circles with their names, types, and capacities. Connections are drawn as lines with capacity labels. Drones are shown as yellow circles with their ID numbers. The window also displays the current turn, its movements, and the number of drones delivered.

If a configured color name is not supported by Pygame, the visualization uses a default color based on the zone type.

## Example

Example map file:

```text
nb_drones: 1
start_hub: start 0 0
hub: middle 1 0
end_hub: goal 2 0
connection: start-middle
connection: middle-goal
```

The terminal displays the paths and the simulation:

```text
Shortest path: start -> middle -> goal
Second path: start -> middle -> goal

Simulation:
D1-middle
D1-goal
```

Each simulation line represents one turn. For example, `D1-middle` means drone 1 moved into the zone named `middle` during that turn.

## Project Files

- `codes/main.py`: Runs all project steps and launches the visualization.
- `codes/parser.py`: Reads and validates the map file.
- `codes/graph.py`: Builds the graph and its neighboring-zone relationships.
- `codes/algorithm.py`: Implements Dijkstra's shortest-path search.
- `codes/second_path.py`: Searches for an alternative path.
- `codes/simulation.py`: Assigns routes to drones and simulates their movements.
- `codes/visualization.py`: Displays the map and drone movements using Pygame.
- `maps/`: Contains example and test map files.

## Resources

- [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Python documentation](https://docs.python.org/3/)
- [Pygame documentation](https://www.pygame.org/docs/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [Flake8 documentation](https://flake8.pycqa.org/)

AI tools were used to explain programming concepts, understand errors, and review code improvements during development.

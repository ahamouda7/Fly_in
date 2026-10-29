
from parser import Parser


class Zone:
    def __init__(self, data: dict):
        self.name = data["name"]
        self.zone_type = data["zone"]
        self.max_drones = data["max_drones"]


class Connection:
    def __init__(self, data: dict):
        self.zone1 = data["connection"][0]
        self.zone2 = data["connection"][1]
        self.max_link_capacity = data["max_link_capacity"]


class Drone:
    def __init__(self, drone_id: int, path: list, position: int):
        self.id = drone_id
        self.path = path
        self.position = position


class Simulation:
    """This class is used to simulate the movements of the drones."""

    def __init__(self, shortest_path: list[str], second_path: list[str]):
        configs = Parser().pars()

        if configs is None:
            raise ValueError("Invalid configuration")

        self.nb_drones = configs["nb_drones"]

        self.start_name = configs["start_hub"]["name"]
        self.end_name = configs["end_hub"]["name"]

        self.zones = {}

        all_zones = (
            [configs["start_hub"]]
            + configs["hubs"]
            + [configs["end_hub"]]
        )

        for data in all_zones:
            zone = Zone(data)
            self.zones[zone.name] = zone

        self.connections = []

        for data in configs["connections"]:
            self.connections.append(Connection(data))

#         if not shortest_path:
#             raise ValueError("No path from start to end")
#
#         if not second_path:
#             second_path = shortest_path

        self.shortest_path = self.prepare_path(shortest_path)
        self.second_path = self.prepare_path(second_path)

    def prepare_path(self, path: list[str]) -> list:
        """Convert zone names to objects and add restricted connections."""
        new_path: list[Zone | Connection] = []

        for i, name in enumerate(path):
            zone = self.zones[name]

            if i > 0 and zone.zone_type == "restricted":
                previous = path[i - 1]

                for connection in self.connections:
                    if {
                        connection.zone1,
                        connection.zone2
                    } == {previous, name}:
                        new_path.append(connection)
                        break
                else:
                    raise ValueError(
                        f"No connection between '{previous}' and '{name}'"
                    )

            new_path.append(zone)

        return new_path

    def zone_is_full(self, zone_name: str | Connection,
                     hubs_size: dict) -> bool:
        """This function checks if the zone is full or not."""
        if isinstance(zone_name, Connection):
            if hubs_size[zone_name] >= zone_name.max_link_capacity:
                return True
            return False

        max_drones = self.zones[zone_name].max_drones
        if hubs_size[zone_name] >= max_drones:
            return True

        return False

    def can_move(self, path: list, position: int,
                 hubs_size: dict, used: dict, reserved: dict) -> bool:
        """This function checks if the drone can move to its next zone."""
        current_stage = path[position]
        next_stage = path[position + 1]

        if isinstance(current_stage, Connection):
            return True

        if isinstance(next_stage, Connection):
            dest_zone = path[position + 2]

            free_space = dest_zone.max_drones - hubs_size[dest_zone.name]

            if free_space == 0 and position + 3 < len(path):
                after = path[position + 3]
                if isinstance(after, Zone) and not self.zone_is_full(
                        after.name, hubs_size):
                    if (
                        hubs_size[dest_zone.name]
                        > reserved.get(dest_zone.name, 0)
                    ):
                        free_space = 1

                    for route in (self.shortest_path, self.second_path):
                        if route != path and (
                            dest_zone in route or after in route
                        ):
                            free_space = 0

            link_free_space = (
                next_stage.max_link_capacity - used.get(next_stage, 0)
            )

            if free_space <= 0 or link_free_space <= 0:
                return False

            used[next_stage] = used.get(next_stage, 0) + 1
            reserved[dest_zone.name] = reserved.get(dest_zone.name, 0) + 1

            return True

        for connection in self.connections:
            if {connection.zone1, connection.zone2} == {
                current_stage.name,
                next_stage.name
            }:
                if used.get(connection, 0) >= connection.max_link_capacity:
                    return False

                if self.zone_is_full(next_stage.name, hubs_size):
                    return False

                used[connection] = used.get(connection, 0) + 1
                return True

        return False

    def set_paths_for_drones(self) -> list[Drone]:
        """This function sets the path for every drone."""
        drones = []

        for i in range(self.nb_drones):
            if i % 2 == 0:
                drones.append(Drone(i + 1, self.shortest_path, 0))
            else:
                drones.append(Drone(i + 1, self.second_path, 0))

        return drones

    def simulation(self) -> list[str]:
        """Simulate drone movements and return the output."""
        drones = self.set_paths_for_drones()

        # for drone in drones:
        #     print(
        #         [
        #         drone.id,
        #         [
        #             z.name
        #             if isinstance(z, Zone)
        #             else f"{z.zone1}-{z.zone2}"
        #             for z in drone.path
        #         ],
        #         drone.position
        #         ]
        #     )

        hubs_size: dict[str | Connection, int] = {}

        for zone in self.zones:
            if zone == self.start_name:
                hubs_size[zone] = self.nb_drones
            else:
                hubs_size[zone] = 0

        for connection in self.connections:
            hubs_size[connection] = 0

        # for i in hubs_size:
        #     if isinstance(i, Connection):
        #         print(f"{i.zone1}-{i.zone2}: {hubs_size[i]}")
        #     else:
        #         print(f"{i}: {hubs_size[i]}")

        output = []

        while not all(
            drone.position == len(drone.path) - 1 for drone in drones
        ):
            turn = ""
            used: dict = {}
            reserved: dict = {}

            for drone in drones:
                if drone.path[drone.position] == self.zones[self.end_name]:
                    continue

                if not self.can_move(
                    drone.path,
                    drone.position,
                    hubs_size,
                    used,
                    reserved
                ):
                    continue

                current_stage = drone.path[drone.position]
                next_stage = drone.path[drone.position + 1]

                if isinstance(current_stage, Connection):
                    hubs_size[current_stage] -= 1

                    turn += f"D{drone.id}-{next_stage.name} "
                    drone.position += 1

                elif isinstance(next_stage, Connection):
                    if not self.zone_is_full(next_stage, hubs_size):
                        hubs_size[next_stage] += 1
                        hubs_size[current_stage.name] -= 1
                        hubs_size[
                            drone.path[drone.position + 2].name
                        ] += 1

                        turn += (
                            f"D{drone.id}-{next_stage.zone1}-"
                            f"{next_stage.zone2} "
                        )
                        drone.position += 1

                elif not self.zone_is_full(next_stage.name, hubs_size):
                    hubs_size[next_stage.name] += 1
                    hubs_size[current_stage.name] -= 1

                    turn += f"D{drone.id}-{next_stage.name} "
                    drone.position += 1

            output.append(turn.strip())

        return output


# from algorithm import Dijkstra
# from second_path import Path2
#
# path1 = Dijkstra().algo()
# path2 = Path2().second_path()
#
# Simulation(path1, path2).simulation()


"""Display the Fly_in graph and animate drone movements."""

import pygame
from typing import Any


class Visualizer:
    """Display the graph and animate drone movements."""

    def show_visualization(
        self,
        configs: dict[str, Any],
        output: list[str]
    ) -> None:
        """Initialize the display, graph, drones, and Pygame window."""
        pygame.init()

        self.zones = (
            [configs["start_hub"]] + configs["hubs"] + [configs["end_hub"]]
        )
        self.zones_by_name = {zone["name"]: zone for zone in self.zones}
        self.connections = configs["connections"]
        self.turns = output
        self.turn_index = 0
        self.nb_drones = configs["nb_drones"]

        # 1337 Mac display dimentions: (3000, 1500)
        # My Windows laptop display dimentions: (1400, 700)
        self.screen = pygame.display.set_mode((1400, 700))

        self.font = pygame.font.SysFont("consolas", 30)
        pygame.display.set_caption("Fly-in")

        self.clock = pygame.time.Clock()
        self.drone_image = pygame.image.load("drone.png")
        self.drone_image = pygame.transform.scale(
            self.drone_image,
            (80, 80)
        )
        self.progress = 0.0
        self.speed = 0.05
        self.drone_positions: dict[str, str] = {}

        for drone_id in range(1, self.nb_drones + 1):
            drone_name = f"D{drone_id}"
            self.drone_positions[drone_name] = configs["start_hub"]["name"]

        self.active_moves: dict[str, tuple[str, str]] = {}
        self.camera_x = 0
        self.camera_y = 0
        self.dragging = False

        self.run()

    def to_screen(self, x: float, y: float) -> tuple[int, int]:
        """Convert graph coordinates to screen coordinates."""
        screen_x = int(200 + (x * 250) + self.camera_x)
        screen_y = int(300 - (y * 250) + self.camera_y)
        return screen_x, screen_y

    def draw_zone(
        self,
        name: str,
        x: int,
        y: int
    ) -> None:
        """Draw a zone and its name on the screen."""
        screen_x, screen_y = self.to_screen(x, y)
        try:
            name_color = self.zones_by_name[name].get("color") or "blue"
            color = pygame.Color(name_color)
        except ValueError:
            color = pygame.Color("blue")
        pygame.draw.circle(
            self.screen,
            color,
            (screen_x, screen_y),
            50
        )

        text = self.font.render(
            name,
            True,
            "white"
        )

        text_rect = text.get_rect(
            center=(screen_x, screen_y - 80)
        )

        self.screen.blit(
            text,
            text_rect
        )

    def draw_connection(
        self,
        zone1_name: str,
        zone2_name: str,
        connection_type: str
    ) -> None:
        """Draw a connection between two zones."""
        zone1 = self.zones_by_name[zone1_name]
        zone2 = self.zones_by_name[zone2_name]

        x1, y1 = zone1["x"], zone1["y"]
        x2, y2 = zone2["x"], zone2["y"]

        screen_x1, screen_y1 = self.to_screen(x1, y1)
        screen_x2, screen_y2 = self.to_screen(x2, y2)

        pygame.draw.line(
            self.screen,
            "gray",
            (screen_x1, screen_y1),
            (screen_x2, screen_y2),
            2
        )

        middle_x = (screen_x1 + screen_x2) / 2
        middle_y = (screen_y1 + screen_y2) / 2
        if (
            connection_type == "normal"
            or connection_type == "priority"
        ):
            text = self.font.render(
                "1",
                True,
                "white"
            )

            text_rect = text.get_rect(
                center=(middle_x, middle_y)
            )

            self.screen.blit(
                text,
                text_rect
            )
        elif connection_type == "restricted":
            text = self.font.render(
                "2",
                True,
                "white"
            )

            text_rect = text.get_rect(
                center=(middle_x, middle_y)
            )

            self.screen.blit(
                text,
                text_rect
            )

    def draw_drone(
        self,
        id: str,
        x: float,
        y: float
    ) -> None:
        """Draw a drone and its name at the given position."""
        screen_x, screen_y = self.to_screen(x, y)

        rect = self.drone_image.get_rect(
            center=(screen_x, screen_y)
        )

        self.screen.blit(
            self.drone_image,
            rect
        )

        text = self.font.render(
            id,
            True,
            "gray"
        )

        text_rect = text.get_rect(
            center=(screen_x, screen_y + 30)
        )

        self.screen.blit(
            text,
            text_rect
        )

    def middle_coordinates(self, two_zones: str) -> tuple[float, float]:
        """Find the middle point between two connected zones."""
        if '-' in two_zones:
            first_zone_name, second_zone_name = two_zones.split('-')
            first_zone = self.zones_by_name[first_zone_name]
            second_zone = self.zones_by_name[second_zone_name]
            x1, y1 = first_zone["x"], first_zone["y"]
            x2, y2 = second_zone["x"], second_zone["y"]
        else:
            raise ValueError("Expected two zone names separated by '-'")
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    def run(self) -> None:
        """Run the display loop and handle animation and user input."""
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN and not self.active_moves:
                    if event.key == pygame.K_SPACE:
                        if self.turn_index < len(self.turns):
                            moves = self.turns[self.turn_index].strip().split()
                            for move in moves:
                                drone, destination = move.split('-', 1)

                                self.active_moves[drone] = (
                                    self.drone_positions[drone],
                                    destination
                                )
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    self.dragging = True
                if (
                    event.type == pygame.MOUSEBUTTONUP
                    and event.button == 1
                ):
                    self.dragging = False
                if (
                    event.type == pygame.MOUSEMOTION
                    and self.dragging
                ):
                    dx, dy = event.rel

                    self.camera_x += dx
                    self.camera_y += dy

            self.screen.fill((30, 30, 30))

            for connection in self.connections:
                self.draw_connection(
                    connection["connection"][0],
                    connection["connection"][1],
                    connection_type=(
                        self.zones_by_name[connection["connection"][1]]["zone"]
                    )
                )

            for zone in self.zones:
                self.draw_zone(zone["name"], zone["x"], zone["y"])

            for drone, zone_name in self.drone_positions.items():
                if drone not in self.active_moves:
                    if '-' in zone_name:
                        x, y = self.middle_coordinates(zone_name)
                    else:
                        zone = self.zones_by_name[zone_name]
                        x, y = zone["x"], zone["y"]
                    self.draw_drone(
                        drone,
                        x,
                        y
                    )

            if self.active_moves:
                for drone, movement in self.active_moves.items():
                    start_name, end_name = movement

                    start_x: float
                    start_y: float
                    end_x: float
                    end_y: float

                    if '-' in start_name:
                        start_x, start_y = self.middle_coordinates(start_name)
                        end_zone = self.zones_by_name[end_name]
                        end_x, end_y = end_zone["x"], end_zone["y"]

                    elif '-' in end_name:
                        start_zone = self.zones_by_name[start_name]
                        start_x, start_y = start_zone["x"], start_zone["y"]
                        end_x, end_y = self.middle_coordinates(end_name)
                    else:
                        start_zone = self.zones_by_name[start_name]
                        end_zone = self.zones_by_name[end_name]
                        start_x, start_y = start_zone["x"], start_zone["y"]
                        end_x, end_y = end_zone["x"], end_zone["y"]
                    x = start_x + (end_x - start_x) * self.progress
                    y = start_y + (end_y - start_y) * self.progress
                    self.draw_drone(
                        drone,
                        x,
                        y
                    )
                self.progress += self.speed
            if self.progress >= 1.0:
                for drone, movement in self.active_moves.items():
                    start_name, end_name = movement
                    self.drone_positions[drone] = end_name
                self.active_moves.clear()
                self.progress = 0.0
                self.turn_index += 1

            turn_text = self.font.render(
                f"Turns: ({self.turn_index}/{len(self.turns)})",
                True,
                "white"
            )

            self.screen.blit(
                turn_text,
                (20, 20)
            )
            pygame.display.flip()
            self.clock.tick(120)

        pygame.quit()


"""Simple Pygame map for viewing Fly_in simulation turns."""

import math
import pygame
from typing import Any


class Visualizer:

    @staticmethod
    def build_frames(configs: dict[str, Any], output: list[str]
                     ) -> list[dict[int, str | tuple[str, str]]]:
        """Get every drone's location after each simulation turn."""
        start = configs["start_hub"]["name"]
        drones: dict[int, str | tuple[str, str]] = {
            i: start for i in range(1, configs["nb_drones"] + 1)
        }
        frames = [drones.copy()]

        for turn in output:
            for move in turn.split():
                drone, destination = move.split("-", 1)
                parts = destination.split("-")
                drones[int(drone[1:])] = (
                    (parts[0], parts[1]) if len(parts) == 2 else parts[0]
                )
            frames.append(drones.copy())

        return frames

    @staticmethod
    def zone_color(zone: dict[str, Any]) -> tuple[int, int, int]:
        """Use the given color, or a default when Pygame cannot read it."""
        name = zone.get("color")
        if name:
            try:
                value = pygame.Color(name)
                return value.r, value.g, value.b
            except ValueError:
                pass
        return {
            "normal": (170, 170, 170),
            "priority": (70, 150, 245),
            "restricted": (245, 125, 80),
            "blocked": (70, 70, 70),
        }.get(zone["zone"], (170, 170, 170))

    def show_visualization(self, configs: dict[str, Any],
                           output: list[str]) -> None:
        """Show zones, connections and drone movements, one turn at a time."""

        pygame.init()
        screen = pygame.display.set_mode((1000, 700))
        pygame.display.set_caption("Fly_in")
        font = pygame.font.Font(None, 25)
        small = pygame.font.Font(None, 15)

        zones = [configs["start_hub"]] + configs["hubs"] + [configs["end_hub"]]
        xs = [zone["x"] for zone in zones]
        ys = [zone["y"] for zone in zones]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        points = {
            zone["name"]: (
                110 + int((780 * (zone["x"] - min_x)) / max(1, max_x - min_x)),
                130 + int((430 * (max_y - zone["y"])) / max(1, max_y - min_y)),
            )
            for zone in zones
        }
        frames = self.build_frames(configs, output)
        end = configs["end_hub"]["name"]
        turn = 0
        running = True

        def write(message: str, x: int, y: int, tiny: bool = False,
                  color: tuple = (240, 240, 240)) -> None:
            face = small if tiny else font
            screen.blit(face.render(message, True, color), (x, y))

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_RIGHT:
                        turn = min(turn + 1, len(output))
                    elif event.key == pygame.K_LEFT:
                        turn = max(turn - 1, 0)
                    elif event.key == pygame.K_r:
                        turn = 0

            screen.fill((25, 25, 30))
            write(f"Turn {turn}/{len(output)} | Left/Right: turn | "
                  "R: reset | Esc: quit", 20, 15)
            movement = output[turn - 1] if turn else "start"
            write("Movement: " + movement, 20, 45, True)
            delivered = sum(
                location == end for location in frames[turn].values()
            )
            write(f"Delivered: {delivered}/{configs['nb_drones']}", 20, 70)

            for connection in configs["connections"]:
                a, b = connection["connection"]
                pygame.draw.line(
                    screen, (130, 130, 130), points[a], points[b], 2
                )
                x = (points[a][0] + points[b][0]) // 2
                y = (points[a][1] + points[b][1]) // 2
                write(str(connection["max_link_capacity"]), x + 5, y + 5, True)

            for zone in zones:
                name = zone["name"]
                x, y = points[name]
                pygame.draw.circle(screen, self.zone_color(zone), (x, y), 18)
                pygame.draw.circle(screen, (0, 0, 0), (x, y), 18, 2)
                write(name, x - 20, y + 22, True)
                info = f"{zone['zone']} cap:{zone['max_drones']}"
                write(info, x - 30, y + 40, True)
                if zone.get("color"):
                    write(f"color:{zone['color']}", x - 30, y + 56, True)

            groups: dict[str | tuple[str, str], list[int]] = {}
            for drone_id, location in frames[turn].items():
                groups.setdefault(location, []).append(drone_id)

            for location, ids in groups.items():
                if isinstance(location, tuple):
                    a, b = points[location[0]], points[location[1]]
                    x, y = (a[0] + b[0]) // 2, (a[1] + b[1]) // 2
                else:
                    x, y = points[location]
                for index, drone_id in enumerate(ids):
                    angle = 2 * math.pi * (index % 10) / min(len(ids), 10)
                    radius = 29 + (index // 10) * 23
                    dx = int(math.cos(angle) * radius)
                    dy = int(math.sin(angle) * radius)
                    drone_pos = (x + dx, y + dy)
                    pygame.draw.circle(screen, (255, 230, 90), drone_pos, 11)
                    pygame.draw.circle(
                        screen,
                        (0, 0, 0),
                        (x + dx, y + dy),
                        11,
                        1
                    )
                    write(
                        str(drone_id),
                        x + dx - 6, y + dy - 7,
                        True,
                        (20, 20, 20)
                    )

            pygame.display.flip()
            pygame.time.wait(35)

        pygame.quit()

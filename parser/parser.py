from typing import Dict, Any, Optional
import matplotlib.colors as color
import sys


class TokenError(Exception):
    pass


class InvalidConf(Exception):
    pass


class MissingConf(Exception):
    pass


def comment_index(s: str) -> int:
    i = 0
    for c in s:
        if c == '#':
            return i
        i += 1
    return -1


def is_known_color(may_color: str) -> bool:
    if may_color == "rainbow":
        return True
    return may_color in color.CSS4_COLORS


def pars() -> Optional[Dict[str, Any]]:
    try:
        if len(sys.argv) != 2:
            raise TokenError(
                "Invalid tokens <python3 a_maze_ing.py config.txt>"
                )

        with open(sys.argv[1]) as file:
            get_conf = file.read().split("\n")
            conf_lists = []
            conf_dict: Dict[str, Any] = {
                "nb_drones": 0,
                "start_hub": {},
                "hubs": [],
                "end_hub": {},
                "connections": []
                }

            for line in get_conf:
                if line.strip() != "" and line.strip()[0] != '#':
                    conf_lists.append(line.split(":", 1))

            if conf_lists[0][0].lower().strip() != "nb_drones":
                raise InvalidConf(
                    "Invalid config, first line must be 'nb_drones'"
                    )

            for a_list in conf_lists:
                if len(a_list) == 1:
                    raise InvalidConf(
                        "Invalid config, it does not respect "
                        "the 'KEY=VALUE' format"
                        )
                if '#' in a_list[1]:
                    i = comment_index(a_list[1])
                    a_list[1] = a_list[1][:i]

                if (
                    a_list[0].lower().strip() == "nb_drones"
                    or a_list[0].lower().strip() == "start_hub"
                    or a_list[0].lower().strip() == "end_hub"
                ):
                    conf_dict[a_list[0].lower().strip()] = (
                        a_list[1].lower().strip()
                        )
                elif a_list[0].lower().strip() == "hub":
                    conf_dict["hubs"].append(a_list[1].lower().strip())
                else:
                    conf_dict["connections"].append(a_list[1].lower().strip())

            keys = ["nb_drones", "start_hub", "hubs", "end_hub",
                    "connections"]
            for k in conf_dict:
                if k not in keys:
                    raise InvalidConf(f"Invalid config '{k}', is not a key")
            for k in keys:
                if k not in list(conf_dict):
                    raise MissingConf(f"Missing the '{k}' config")

            nb_drones = conf_dict["nb_drones"]
            start_hub = conf_dict["start_hub"]
            hubs = conf_dict["hubs"]
            end_hub = conf_dict["end_hub"]
            connections = conf_dict["connections"]

            nb_drones = conf_dict["nb_drones"] = int(nb_drones)
            if nb_drones < 0:
                raise InvalidConf("Invalid config, nb_drones must be positive")

            start_hub = start_hub.split(" ")
            end_hub = end_hub.split(" ")
            # if len(start_hub) != 4 or len(end_hub) != 4:
            #     raise InvalidConf(
            #         "Invalid config, Hubs must include 3 parameters "
            #         "(name, x, y)"
            #         )

            for i in range(len(hubs)):
                hubs[i] = hubs[i].split(" ")
                # if len(hubs[i]) != 4:
                #     raise InvalidConf(
                #         "Invalid config, Hubs must include 3 parameters "
                #         "(name, x, y)"
                #         )

            s_brackets = start_hub[3:]
            for i in range(len(s_brackets)):
                s_brackets[i] = s_brackets[i].lower().strip("[]").split("=")
            start_hub = {
                "start": start_hub[0],
                "x": int(start_hub[1]),
                "y": int(start_hub[2]),
                }
            if start_hub["x"] < 0 or start_hub["y"] < 0:
                raise InvalidConf("Invalid config, x & y must be positive")
            for i in range(len(s_brackets)):
                if s_brackets[i][0] == "max_drones":
                    start_hub[s_brackets[i][0]] = int(s_brackets[i][1])
                    if (
                        start_hub[s_brackets[i][0]] < 0
                        or start_hub[s_brackets[i][0]] < 0
                    ):
                        raise InvalidConf(
                            "Invalid config, max_drones must be positive"
                            )
                elif s_brackets[i][0] == "color":
                    if is_known_color(s_brackets[i][1]):
                        continue
                    else:
                        raise InvalidConf(
                            f"Invalid config '{s_brackets[i][1]}', "
                            "is not a color"
                            )
                elif s_brackets[i][0] == "zone":
                    zones = ["normal", "restricted", "priority", "blocked"]
                    if start_hub[s_brackets[i][0]] not in zones:
                        raise InvalidConf(
                            f"Invalid config '{s_brackets[i][1]}', "
                            "is not a zone"
                            )
                    start_hub[s_brackets[i][0]] = s_brackets[i][1]
                else:
                    raise InvalidConf(
                        f"Invalid config '{s_brackets[i][1]}', "
                        "is not available"
                        )

            for i in range(len(hubs)):
                s_brackets = hubs[i][3:]
                for j in range(len(s_brackets)):
                    s_brackets[j] = (
                        s_brackets[j].lower().strip("[]").split("=")
                        )
                hubs[i] = {
                    "start": hubs[i][0],
                    "x": int(hubs[i][1]),
                    "y": int(hubs[i][2]),
                    }
                if hubs[i]["x"] < 0 or hubs[i]["y"] < 0:
                    raise InvalidConf("Invalid config, x & y must be positive")
                for j in range(len(s_brackets)):
                    if s_brackets[j][0] == "max_drones":
                        hubs[i][s_brackets[j][0]] = int(s_brackets[j][1])
                        if (
                            hubs[i][s_brackets[j][0]] < 0
                            or hubs[i][s_brackets[j][0]] < 0
                        ):
                            raise InvalidConf(
                                "Invalid config, max_drones must be positive"
                                )
                    elif s_brackets[j][0] == "color":
                        if is_known_color(s_brackets[j][1]):
                            continue
                        else:
                            raise InvalidConf(
                                f"Invalid config '{s_brackets[j][1]}', "
                                "is not a color"
                                )
                    elif s_brackets[j][0] == "zone":
                        zones = ["normal", "restricted", "priority", "blocked"]
                        if hubs[i][s_brackets[j][0]] not in zones:
                            raise InvalidConf(
                                f"Invalid config '{s_brackets[j][1]}', "
                                "is not a zone"
                                )
                        hubs[i][s_brackets[j][0]] = s_brackets[j][1]
                    else:
                        raise InvalidConf(
                            f"Invalid config '{s_brackets[j][1]}', "
                            "is not available"
                            )

            s_brackets = end_hub[3:]
            for i in range(len(s_brackets)):
                s_brackets[i] = s_brackets[i].lower().strip("[]").split("=")
            end_hub = {
                "start": end_hub[0],
                "x": int(end_hub[1]),
                "y": int(end_hub[2]),
                }
            if end_hub["x"] < 0 or end_hub["y"] < 0:
                raise InvalidConf("Invalid config, x & y must be positive")
            for i in range(len(s_brackets)):
                if s_brackets[i][0] == "max_drones":
                    end_hub[s_brackets[i][0]] = int(s_brackets[i][1])
                    if (
                        end_hub[s_brackets[i][0]] < 0
                        or end_hub[s_brackets[i][0]] < 0
                    ):
                        raise InvalidConf(
                            "Invalid config, max_drones must be positive"
                            )
                elif s_brackets[i][0] == "color":
                    if is_known_color(s_brackets[i][1]):
                        continue
                    else:
                        raise InvalidConf(
                            f"Invalid config '{s_brackets[i][1]}', "
                            "is not a color"
                            )
                elif s_brackets[i][0] == "zone":
                    zones = ["normal", "restricted", "priority", "blocked"]
                    if end_hub[s_brackets[i][0]] not in zones:
                        raise InvalidConf(
                            f"Invalid config '{s_brackets[i][1]}', "
                            "is not a zone"
                            )
                    end_hub[s_brackets[i][0]] = s_brackets[i][1]
                else:
                    raise InvalidConf(
                        f"Invalid config '{s_brackets[i][1]}', "
                        "is not available"
                        )

            for i in range(len(connections)):
                connections[i] = connections[i].replace("-", " ").split(" ")
                if len(connections[i]) != 2 and len(connections[i]) != 3:
                    raise InvalidConf(
                        "Invalid config, a connection needs 2 hubs"
                        )
                if len(connections[i]) == 3:
                    link_capacity = (
                        connections[i][2].strip("[]").lower().split("=")
                        )
                    link_capacity[1] = int(link_capacity[1])
                    if link_capacity[1] < 0:
                        raise InvalidConf(
                            "Invalid config, "
                            "max_link_capacity must be positive"
                            )
                    connections[i] = {
                        "connection": (connections[i][0], connections[i][1]),
                        "max_link_capacity": link_capacity[1]
                        },
                else:
                    connections[i] = {
                        "connection": (connections[i][0], connections[i][1])
                        }

            conf_dict["nb_drones"] = nb_drones
            conf_dict["start_hub"] = start_hub
            conf_dict["end_hub"] = end_hub
            conf_dict["hubs"] = hubs
            conf_dict["connections"] = connections
    except Exception as e:
        print(f"ERROR: {e}")
        return None

    return conf_dict


if pars():
    print(pars())

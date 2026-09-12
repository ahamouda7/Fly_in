from typing import Dict, Any, Optional
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


def pars() -> Optional[Dict[str, Any]]:
    try:
        if len(sys.argv) != 2:
            raise TokenError(
                "Invalid tokens <python3 a_maze_ing.py config.txt>"
                )

        with open(sys.argv[1]) as file:
            get_conf = file.read().split("\n")
            conf_lists = []
            conf_dict: Dict[str, Any] = {}

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
                conf_dict[a_list[0].lower().strip()] = a_list[1].lower().strip()

            keys = ["nb_drones", "start_hub", "hub", "end_hub",
                    "connection"]
            for k in conf_dict:
                if k not in keys:
                    raise InvalidConf(f"Invalid config '{k}', is not a key")
            for k in keys:
                if k not in list(conf_dict):
                    raise MissingConf(f"Missing the '{k}' config")

            nb_drones = conf_dict["nb_drones"]
            start_hub = conf_dict["start_hub"]
            hub = conf_dict["hub"]
            end_hub = conf_dict["end_hub"]
            connection = conf_dict["connection"]

            nb_drones = conf_dict["nb_drones"] = int(nb_drones)

            start_hub = start_hub.split(" ")
            end_hub = end_hub.split(" ")
            hub = hub.split(" ")
            if len(start_hub) != 4 or len(end_hub) != 4 or len(hub) != 4:
                raise InvalidConf(
                    "Invalid config, Hubs must include 3 parameters "
                    "(name, x, y)"
                    )

            connection = connection.split("-")
            if len(connection) != 2:
                raise InvalidConf("Invalid config, a connection needs 2 hubs")

            conf_dict["nb_drones"] = nb_drones
            conf_dict["start_hub"] = start_hub
            conf_dict["end_hub"] = end_hub
            conf_dict["hub"] = hub
            conf_dict["connection"] = connection
    except Exception as e:
        print(f"ERROR: {e}")
        return None

    return conf_dict


if pars():
    print(pars())

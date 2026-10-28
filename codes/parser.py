from typing import Dict, Any, List, Optional
import matplotlib.colors as color
import sys


class TokenError(Exception):
    pass


class InvalidConf(Exception):
    pass


class MissingConf(Exception):
    pass


class Parser:
    @staticmethod
    def comment_index(s: str) -> int:
        i = 0
        for c in s:
            if c == '#':
                return i
            i += 1
        return -1

    @staticmethod
    def is_known_color(may_color: str) -> bool:
        if may_color == "rainbow":
            return True
        return may_color in color.CSS4_COLORS

    @staticmethod
    def extract_bracket_tags(raw: str, where: str) -> List[str]:
        """Pull the raw 'key=value' tags out of an optional [...] block.

        Whitespace right after '[', right before ']', or between tags is
        ignored. An empty/missing block returns no tags. Anything left
        after the closing ']' is a real error, not whitespace noise.
        """
        raw = (raw or "").strip()
        if raw == "":
            return []
        if not raw.startswith("["):
            raise InvalidConf(
                f"Invalid config in {where}, metadata must start with '['"
                )
        close_idx = raw.rfind("]")
        if close_idx == -1:
            raise InvalidConf(
                f"Invalid config in {where}, metadata is missing a closing ']'"
                )
        extra = raw[close_idx + 1:].strip()
        if extra:
            raise InvalidConf(
                f"Invalid config in {where}, unexpected content "
                f"'{extra}' after ']'"
                )
        return raw[1:close_idx].split()

    @staticmethod
    def collapse_bracket_spaces(text: str) -> str:
        """Remove spaces that fall between '[' and ']' in a string."""
        start = text.find("[")
        end = text.find("]")
        if start == -1 or end == -1 or end <= start:
            return text
        inside = text[start:end + 1]
        inside = inside.replace(" ", "")
        return text[:start] + inside + text[end + 1:]

    @staticmethod
    def pars() -> Optional[Dict[str, Any]]:
        try:
            if len(sys.argv) != 2:
                raise TokenError(
                    "Invalid tokens <python3 parser.py config.txt>"
                    )

            with open(sys.argv[1]) as file:
                get_conf = file.read().split("\n")
                conf_lists = []
                conf_dict: Dict[str, Any] = {
                    "nb_drones": None,
                    "start_hub": None,
                    "hubs": [],
                    "end_hub": None,
                    "connections": []
                    }

                for line in get_conf:
                    if line.strip() != "" and line.strip()[0] != '#':
                        conf_lists.append(line.split(":", 1))

                if len(conf_lists) == 0:
                    raise InvalidConf("Invalid config, file is empty")
                if conf_lists[0][0].lower().strip() != "nb_drones":
                    raise InvalidConf(
                        "Invalid config, first line must be 'nb_drones'"
                        )

                seen_singular = set()
                declared_so_far: set = set()
                for a_list in conf_lists:
                    if len(a_list) == 1:
                        raise InvalidConf(
                            "Invalid config, it does not respect "
                            "the 'KEY=VALUE' format"
                            )
                    if '#' in a_list[1]:
                        i = Parser.comment_index(a_list[1])
                        a_list[1] = a_list[1][:i]

                    key = a_list[0].lower().strip()
                    if key in ("nb_drones", "start_hub", "end_hub"):
                        if key in seen_singular:
                            raise InvalidConf(
                                f"Invalid config, '{key}' must appear "
                                "exactly once, found a duplicate"
                                )
                        seen_singular.add(key)
                        value = a_list[1].strip()
                        conf_dict[key] = value
                        if key in ("start_hub", "end_hub"):
                            tokens = value.split()
                            if tokens:
                                declared_so_far.add(tokens[0])
                    elif key == "hub":
                        value = a_list[1].strip()
                        conf_dict["hubs"].append(value)
                        tokens = value.split()
                        if tokens:
                            declared_so_far.add(tokens[0])
                    elif key == "connection":
                        value = a_list[1].strip()
                        conf_dict["connections"].append(
                            (value, frozenset(declared_so_far))
                            )
                    else:
                        raise InvalidConf(
                            f"Invalid config '{a_list[0].strip()}', "
                            "is not a key"
                            )

                required_keys = ["nb_drones", "start_hub", "end_hub"]
                for k in required_keys:
                    if conf_dict[k] is None:
                        raise MissingConf(f"Missing the '{k}' config")

                nb_drones = conf_dict["nb_drones"]
                start_hub = conf_dict["start_hub"]
                hubs = conf_dict["hubs"]
                end_hub = conf_dict["end_hub"]
                connections = conf_dict["connections"]

                try:
                    nb_drones = conf_dict["nb_drones"] = int(nb_drones)
                except ValueError:
                    raise InvalidConf(
                        "Invalid config, nb_drones must be an integer"
                        )
                if nb_drones <= 0:
                    raise InvalidConf(
                        "Invalid config, nb_drones must be positive"
                        )

                start_hub = start_hub.split(" ", 3)
                end_hub = end_hub.split(" ", 3)

                for i in range(len(hubs)):
                    hubs[i] = hubs[i].split(" ", 3)

                if len(start_hub) < 3:
                    raise InvalidConf(
                        "Invalid config, start_hub must have <name x y>"
                        )
                if "-" in start_hub[0]:
                    raise InvalidConf(
                        "Invalid config, start_hub name must not contain '-'"
                        )
                raw_meta = start_hub[3] if len(start_hub) > 3 else ""
                raw_brackets = Parser.extract_bracket_tags(
                    raw_meta, "start_hub"
                )
                s_brackets: List[List[str]] = []
                for bracket in raw_brackets:
                    parts = bracket.lower().split("=")
                    if len(parts) != 2:
                        raise InvalidConf(
                            "Invalid config in start_hub, "
                            "metadata must be 'key=value'"
                        )
                    s_brackets.append(parts)

                try:
                    start_hub = {
                        "name": start_hub[0],
                        "x": int(start_hub[1]),
                        "y": int(start_hub[2]),
                        }
                except ValueError:
                    raise InvalidConf(
                        "Invalid config, start_hub x/y must be integers"
                        )

                seen_keys = set()
                for i in range(len(s_brackets)):
                    if s_brackets[i][0] in seen_keys:
                        raise InvalidConf(
                            f"Invalid config in start_hub, duplicate "
                            f"metadata key '{s_brackets[i][0]}'"
                            )
                    seen_keys.add(s_brackets[i][0])
                    if s_brackets[i][0] == "max_drones":
                        continue
                    elif s_brackets[i][0] == "color":
                        if Parser.is_known_color(s_brackets[i][1]):
                            start_hub[s_brackets[i][0]] = s_brackets[i][1]
                        else:
                            raise InvalidConf(
                                f"Invalid config '{s_brackets[i][1]}', "
                                "is not a color"
                                )
                    elif s_brackets[i][0] == "zone":
                        zones = ["normal", "restricted", "priority", "blocked"]
                        if s_brackets[i][1] not in zones:
                            raise InvalidConf(
                                f"Invalid config '{s_brackets[i][1]}', "
                                "is not a zone"
                                )
                        start_hub[s_brackets[i][0]] = s_brackets[i][1]
                    else:
                        raise InvalidConf(
                            f"Invalid config, metadata key "
                            f"'{s_brackets[i][0]}' is not available"
                            )
                start_hub["max_drones"] = nb_drones
                if "zone" not in start_hub:
                    start_hub["zone"] = "normal"

                for i in range(len(hubs)):
                    if "-" in hubs[i][0]:
                        raise InvalidConf(
                            f"Invalid config, hub name '{hubs[i][0]}' "
                            "must not contain '-'"
                            )
                    raw_meta = hubs[i][3] if len(hubs[i]) > 3 else ""
                    raw_brackets = Parser.extract_bracket_tags(
                        raw_meta, f"hub '{hubs[i][0]}'"
                    )
                    s_brackets = []
                    for bracket in raw_brackets:
                        parts = bracket.lower().split("=")
                        if len(parts) != 2:
                            raise InvalidConf(
                                "Invalid config in start_hub, "
                                "metadata must be 'key=value'"
                            )
                        s_brackets.append(parts)
                    if len(hubs[i]) < 3:
                        raise InvalidConf(
                            f"Invalid config, hub '{hubs[i][0]}' is missing "
                            "its x or y coordinate"
                            )
                    try:
                        hub_x = int(hubs[i][1])
                        hub_y = int(hubs[i][2])
                    except ValueError:
                        raise InvalidConf(
                            f"Invalid config, hub '{hubs[i][0]}' x and y "
                            "must be integers"
                            )
                    hubs[i] = {
                        "name": hubs[i][0],
                        "x": hub_x,
                        "y": hub_y,
                        }

                    seen_keys = set()
                    for j in range(len(s_brackets)):
                        if s_brackets[j][0] in seen_keys:
                            raise InvalidConf(
                                f"Invalid config in hub '{hubs[i]['name']}', "
                                f"duplicate metadata key '{s_brackets[j][0]}'"
                                )
                        seen_keys.add(s_brackets[j][0])
                        if s_brackets[j][0] == "max_drones":
                            try:
                                hubs[i][s_brackets[j][0]] = (
                                    int(s_brackets[j][1])
                                    )
                            except ValueError:
                                raise InvalidConf(
                                    "Invalid config in hub "
                                    f"'{hubs[i]['name']}', "
                                    "max_drones must be an integer"
                                    )
                            if hubs[i][s_brackets[j][0]] <= 0:
                                raise InvalidConf(
                                    "Invalid config, "
                                    "max_drones must be positive"
                                    )
                        elif s_brackets[j][0] == "color":
                            if Parser.is_known_color(s_brackets[j][1]):
                                hubs[i][s_brackets[j][0]] = s_brackets[j][1]
                            else:
                                raise InvalidConf(
                                    f"Invalid config '{s_brackets[j][1]}', "
                                    "is not a color"
                                    )
                        elif s_brackets[j][0] == "zone":
                            zones = [
                                "normal", "restricted", "priority", "blocked"
                                ]
                            if s_brackets[j][1] not in zones:
                                raise InvalidConf(
                                    f"Invalid config '{s_brackets[j][1]}', "
                                    "is not a zone"
                                    )
                            hubs[i][s_brackets[j][0]] = s_brackets[j][1]
                        else:
                            raise InvalidConf(
                                f"Invalid config, metadata key "
                                f"'{s_brackets[j][0]}' is not available"
                                )
                    if "zone" not in hubs[i]:
                        hubs[i]["zone"] = "normal"
                    if "max_drones" not in hubs[i]:
                        hubs[i]["max_drones"] = 1

                if len(end_hub) < 3:
                    raise InvalidConf(
                        "Invalid config, end_hub must have <name x y>"
                        )
                if "-" in end_hub[0]:
                    raise InvalidConf(
                        "Invalid config, end_hub name must not contain '-'"
                        )
                raw_meta = end_hub[3] if len(end_hub) > 3 else ""
                raw_brackets = Parser.extract_bracket_tags(raw_meta, "end_hub")
                s_brackets = []
                for bracket in raw_brackets:
                    parts = bracket.lower().split("=")
                    if len(parts) != 2:
                        raise InvalidConf(
                            "Invalid config in start_hub, "
                            "metadata must be 'key=value'"
                        )
                    s_brackets.append(parts)
                try:
                    end_hub = {
                        "name": end_hub[0],
                        "x": int(end_hub[1]),
                        "y": int(end_hub[2]),
                        }
                except ValueError:
                    raise InvalidConf(
                        "Invalid config, end_hub x/y must be integers"
                        )

                seen_keys = set()
                for i in range(len(s_brackets)):
                    if s_brackets[i][0] == "max_drones":
                        continue
                    if s_brackets[i][0] in seen_keys:
                        raise InvalidConf(
                            f"Invalid config in end_hub, duplicate "
                            f"metadata key '{s_brackets[i][0]}'"
                            )
                    seen_keys.add(s_brackets[i][0])
                    if s_brackets[i][0] == "color":
                        if Parser.is_known_color(s_brackets[i][1]):
                            end_hub[s_brackets[i][0]] = s_brackets[i][1]
                        else:
                            raise InvalidConf(
                                f"Invalid config '{s_brackets[i][1]}', "
                                "is not a color"
                                )
                    elif s_brackets[i][0] == "zone":
                        zones = ["normal", "restricted", "priority", "blocked"]
                        if s_brackets[i][1] not in zones:
                            raise InvalidConf(
                                f"Invalid config '{s_brackets[i][1]}', "
                                "is not a zone"
                                )
                        end_hub[s_brackets[i][0]] = s_brackets[i][1]
                    else:
                        raise InvalidConf(
                            f"Invalid config, metadata key "
                            f"'{s_brackets[i][0]}' is not available"
                            )
                if "zone" not in end_hub:
                    end_hub["zone"] = "normal"
                end_hub["max_drones"] = nb_drones

                all_zones = (
                    [start_hub] + hubs + [end_hub]
                    )
                seen_names = set()
                seen_coords: Dict[Any, str] = {}
                for zone in all_zones:
                    name = zone["name"]
                    coords = (zone["x"], zone["y"])
                    if name in seen_names:
                        raise InvalidConf(
                            f"Invalid config, duplicate zone name '{name}'"
                            )
                    seen_names.add(name)
                    if coords in seen_coords:
                        raise InvalidConf(
                            f"Invalid config, zone '{name}' has the same "
                            f"coordinates {coords} as zone "
                            f"'{seen_coords[coords]}'"
                            )
                    seen_coords[coords] = name

                raw_connections = connections
                connections = []
                connection_allowed = []
                for raw_connection, allowed_names in raw_connections:
                    cleaned = Parser.collapse_bracket_spaces(raw_connection)

                    if "[" in cleaned:
                        connection_part, metadata = cleaned.split("[", 1)

                        if connection_part.count("-") != 1:
                            raise InvalidConf(
                                "Invalid config, a connection must be "
                                "<hub1-hub2 [max_link_capacity=x]>"
                            )

                        metadata = "[" + metadata

                        tags = Parser.extract_bracket_tags(
                            metadata, "connection"
                        )

                        if len(tags) != 1:
                            raise InvalidConf(
                                "Invalid config, a connection must be "
                                "<hub1-hub2 [max_link_capacity=x]>"
                            )

                        connection_part = connection_part.replace("-", " ")
                        cleaned = connection_part + " " + tags[0]

                    else:
                        if cleaned.count("-") != 1:
                            raise InvalidConf(
                                "Invalid config, a connection must be "
                                "<hub1-hub2 [max_link_capacity=x]>"
                            )

                        cleaned = cleaned.replace("-", " ")

                    tokens = cleaned.split()
                    clean_tokens = []
                    for token in tokens:
                        clean_tokens.append(token.strip("[]"))
                    connections.append(clean_tokens)
                    connection_allowed.append(allowed_names)

                seen_connections = set()
                for i in range(len(connections)):
                    if len(connections[i]) != 2 and len(connections[i]) != 3:
                        raise InvalidConf(
                            "Invalid config, a connection must be "
                            "<hub1-hub2 [max_link_capacity=x]>, with (x >= 0)"
                            )
                    hub_a, hub_b = connections[i][0], connections[i][1]
                    if hub_a == hub_b:
                        raise InvalidConf(
                            f"Invalid config, connection '{hub_a}-{hub_b}' "
                            "cannot link a zone to itself"
                            )
                    allowed_names = connection_allowed[i]
                    if (
                        hub_a not in allowed_names
                        or hub_b not in allowed_names
                    ):
                        raise InvalidConf(
                            f"Invalid config, connection '{hub_a}-{hub_b}' "
                            "references a zone that was not defined earlier "
                            "in the file"
                            )
                    pair_key = frozenset((hub_a, hub_b))
                    if pair_key in seen_connections:
                        raise InvalidConf(
                            f"Invalid config, duplicate connection "
                            f"'{hub_a}-{hub_b}'"
                            )
                    seen_connections.add(pair_key)
                    if len(connections[i]) == 3:
                        if "=" not in connections[i][2]:
                            raise InvalidConf(
                                "Invalid config, a connection must be "
                                "<hub1-hub2 [max_link_capacity=x]>, "
                                "with (x >= 0)"
                                )
                        link_capacity = (
                            connections[i][2].strip("[]").lower().split("=")
                            )
                        if (
                            len(link_capacity) != 2
                            or link_capacity[0] != "max_link_capacity"
                        ):
                            raise InvalidConf(
                                "Invalid config, a connection must be "
                                "<hub1-hub2 [max_link_capacity=x]>, "
                                "with (x >= 0)"
                                )
                        try:
                            link_capacity[1] = int(link_capacity[1])
                        except ValueError:
                            raise InvalidConf(
                                "Invalid config, "
                                "max_link_capacity must be an integer"
                                )
                        if link_capacity[1] <= 0:
                            raise InvalidConf(
                                "Invalid config, "
                                "max_link_capacity must be positive"
                                )
                        connections[i] = {
                            "connection": (
                                connections[i][0], connections[i][1]
                            ),
                            "max_link_capacity": link_capacity[1]
                            }
                    else:
                        connections[i] = {
                            "connection": (
                                connections[i][0], connections[i][1]
                            ),
                            "max_link_capacity": 1
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


# if __name__ == "__main__":
#     print(Parser.pars())

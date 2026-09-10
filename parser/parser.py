"""Configuration file parsing module.

Parses and validates maze configuration from a text file provided as a
command-line argument. Handles KEY=VALUE format with comment support.
"""

from typing import Dict, Any, Optional
import sys


class TokenError(Exception):
    """Exception raised for invalid command-line arguments."""
    pass


class InvalidConf(Exception):
    """Exception raised for invalid configuration values."""
    pass


class MissingConf(Exception):
    """Exception raised for missing required configuration keys."""
    pass


def comment_index(s: str) -> int:
    """Find the index of the first comment character in a string.

    Searches for the '#' character which marks the start of a comment.

    Args:
        s: String to search for comment character.

    Returns:
        Index of the first '#' character, or -1 if not found.
    """
    i = 0
    for c in s:
        if c == '#':
            return i
        i += 1
    return -1


def pars() -> Optional[Dict[str, Any]]:
    """Parse and validate maze configuration from a file.

    Reads a configuration file provided as a command-line argument in
    KEY=VALUE format (one per line). Validates all required keys, data types,
    and value ranges for maze generation. Supports comments (lines starting
    with '#' or values with trailing '#comment').

    Required configuration keys:
        WIDTH: Integer >= 9, maze width in cells
        HEIGHT: Integer >= 7, maze height in cells
        ENTRY: Two comma-separated integers (x,y), maze entry point
        EXIT: Two comma-separated integers (x,y), maze exit point
        OUTPUT_FILE: String, output filename (cannot match program files)
        PERFECT: Boolean ("True"/"False" or 1/0), maze generation mode
        SEED: Optional integer or None, random seed for reproducibility

    File format example:
        WIDTH=20
        HEIGHT=20
        ENTRY=0,0
        EXIT=19,19
        OUTPUT_FILE=maze.txt
        PERFECT=False
        SEED=42  # Optional

    Returns:
        Dictionary with validated configuration values with uppercase keys,
        or None if parsing or validation fails.

    Raises:
        TokenError: If command-line arguments are invalid.
        InvalidConf: If configuration values are invalid or out of range.
        MissingConf: If required configuration keys are missing.

    Example:
        conf = pars()
        if conf:
            width = conf["WIDTH"]
            height = conf["HEIGHT"]
    """
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
                    conf_lists.append(line.split("=", 1))

            for a_list in conf_lists:
                if len(a_list) == 1:
                    raise InvalidConf(
                        "Invalid config, it does not respect "
                        "the 'KEY=VALUE' format"
                        )
                if '#' in a_list[1]:
                    i = comment_index(a_list[1])
                    a_list[1] = a_list[1][:i]
                conf_dict[a_list[0].upper().strip()] = a_list[1].strip()

            keys = ["WIDTH", "HEIGHT", "ENTRY", "EXIT",
                    "OUTPUT_FILE", "PERFECT", "SEED"]
            for k in conf_dict.keys():
                if k not in keys:
                    raise InvalidConf(f"Invalid config '{k}', is not a key")
            keys.remove("SEED")
            for k in keys:
                if k not in list(conf_dict.keys()):
                    raise MissingConf(f"Missing the '{k}' config")

            width = conf_dict["WIDTH"]
            height = conf_dict["HEIGHT"]
            entry = conf_dict["ENTRY"]
            exit = conf_dict["EXIT"]
            output_file = conf_dict["OUTPUT_FILE"]
            perfect = conf_dict["PERFECT"]
            if "SEED" in conf_dict:
                seed = conf_dict["SEED"]

            width = conf_dict["WIDTH"] = int(width)
            height = conf_dict["HEIGHT"] = int(height)

            entry = entry.split(",")
            exit = exit.split(",")
            if len(entry) != 2 or len(exit) != 2:
                raise InvalidConf(
                    "Invalid config, Entry and Exit must include 2 coordinates"
                    )

            en1 = int(entry[0])
            en2 = int(entry[1])
            entry = conf_dict["ENTRY"] = (en1, en2)

            ex1 = int(exit[0])
            ex2 = int(exit[1])
            exit = conf_dict["EXIT"] = (ex1, ex2)

            files_names = [
                "a_maze_ing.py",
                "config.txt",
                "Makefile",
                "maze_output.py",
                "parsing.py"
                ]
            if output_file in files_names:
                # conf_dict["OUTPUT_FILE"] = "output.txt"
                raise InvalidConf(
                    f"Invalid config {output_file}, output file name "
                    "must be different than other program files names"
                    )

            booleen = ["True", "False"]
            try:
                perfect = perfect.capitalize()
                if perfect in booleen:
                    if perfect == "True":
                        conf_dict["PERFECT"] = True
                    elif perfect == "False":
                        conf_dict["PERFECT"] = False
                elif int(perfect) == 1 or int(perfect) == 0:
                    if int(perfect) == 1:
                        conf_dict["PERFECT"] = True
                    else:
                        conf_dict["PERFECT"] = False
                else:
                    raise InvalidConf(
                        f"Invalid config '{perfect}', "
                        "it is not a bool() value"
                        )
            except ValueError:
                print(
                    f"ERROR: Invalid config '{perfect}', "
                    "it is not a bool() value"
                    )
                sys.exit()

            if "SEED" not in conf_dict:
                seed = conf_dict["SEED"] = None
            if (seed is not None) and (seed.strip() == ""):
                raise InvalidConf(
                    "Invalid config, it does not respect "
                    "the 'KEY=VALUE' format"
                    )

            if width <= 0 or height <= 0:
                raise InvalidConf(
                    "Invalid config, width and height must be greater than '0'"
                    )

            if (
                ((en1 < 0) or (en2 < 0))
                or ((ex1 < 0) or (ex2 < 0))
            ):
                raise InvalidConf(
                    "Invalid config, coordinates must be positive"
                    )

            if (
                ((en1 >= width) or (en2 >= height))
                or ((ex1 >= width) or (ex2 >= height))
            ):
                raise InvalidConf(
                    "Invalid config, a coordinate is out of range"
                    )

            if entry == exit:
                raise InvalidConf(
                    "Invalid config, Entry and Exit must be different"
                    )
    except Exception as e:
        print(f"ERROR: {e}")
        return None

    return conf_dict
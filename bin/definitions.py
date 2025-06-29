#!/usr/bin/env python3

import json
import os
import striker
import exception


def get_toggle_suffix():
    # Check if the state file exists
    if os.path.exists(striker.FILE_DEFINITION_TOGGLE):
        with open(striker.FILE_DEFINITION_TOGGLE, "r") as f:
            last = f.read().strip()
    else:
        last = ""

    # Toggle logic
    next_suffix = "_b" if last == "_a" else "_a"

    # Write new state
    with open(striker.FILE_DEFINITION_TOGGLE, "w") as f:
        f.write(next_suffix)

    return next_suffix == "_a"


#
#
#
def get_line(offset, col1, col2, col3):
    return f"${{goto {offset + 10}}}{col1}${{goto {offset + 120}}}{col2}${{goto {offset + 260}}}{col3}"


#
#
#
def get_line5(color, col1, col2, col3, col4, col5):
    return f"${{goto 20}}${{color {color}}}{col1:<16}{col2:<20}{col3:<12}${{color white}}                  | {col4:<20}{col5:<30}\n"


#
#
#
def get_definitions(toggle):
    try:
        if toggle:
            with open(striker.FILE_DEFINITION_DATA, "r", encoding="utf-8") as f:
                definitions = json.load(f)

            result = ""
            for key, value in definitions.items():
                lines = striker.wrap_text(value, 120)
                for line in lines:
                    result += striker.get_line_align_left2(key, line) + "\n"
                    # print(f"${{goto 10}}${{alignc}}${{font4}}${{color red}}{line}")

            return result
        else:
            result = ""
            result += get_line5(
                "Yellow",
                "Spectral Type",
                "Temperature (K)",
                "Color",
                "Luminosity Class",
                "Description",
            )
            result += f"${{goto 10}}${{color gray}}${{hr 1}}\n"
            result += get_line5(
                "Blue",
                "O",
                "> 30,000",
                "Blue",
                "I",
                "Supergiant",
            )
            result += get_line5(
                "#aabfff",
                "B",
                "  10,000 - 30,000",
                "Blue-white",
                "II",
                "Bright giant",
            )
            result += get_line5(
                "White",
                "A",
                "   7,500 - 10,000",
                "White",
                "III",
                "Giant",
            )
            result += get_line5(
                "#ffffe0",
                "F",
                "   6,000 -  7,500",
                "Yellow-White",
                "IV",
                "Sub-giant",
            )
            result += get_line5(
                "Yellow",
                "G",
                "   5,200 -  6,000",
                "Yellow",
                "V",
                "Main Sequence (Dwarf)",
            )
            result += get_line5(
                "Orange",
                "K",
                "   3,700 -  5,200",
                "Orange",
                "VI",
                "Sub-dwarf",
            )
            result += get_line5(
                "Red",
                "M",
                "<  3,700",
                "Red",
                "VII",
                "White-dwarf (Dead core)",
            )
            return result
    except FileNotFoundError:
        raise exception.StrikerException(
            f"File not found: {striker.FILE_DEFINITION_DATA}"
        )
    except PermissionError:
        raise exception.StrikerException(
            f"Permission denied: {striker.FILE_DEFINITION_DATA}"
        )
    except Exception as e:
        raise exception.StrikerException(f"Unexpected error: {e}")


#
#
#
if __name__ == "__main__":
    print(striker.get_section_title("Definitions", ""))
    try:
        print(get_definitions(get_toggle_suffix()))
    except exception.StrikerException as e:
        print(exception.StrikerException.get_message(e))

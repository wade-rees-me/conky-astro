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
    return f"${{goto {offset + 30}}}{col1}${{goto {offset + 120}}}{col2}${{goto {offset + 260}}}{col3}"


#
#
#
def get_definitions(toggle):
    try:
        if toggle:
            if "CONKY_HOME" not in os.environ:
                raise EnvironmentError("CONKY_HOME environment variable is not set.")

            FILE_NAME = os.path.join(
                os.environ["CONKY_HOME"], "data", "definitions.json"
            )

            with open(FILE_NAME, "r", encoding="utf-8") as f:
                definitions = json.load(f)

            result = ""
            for key, value in definitions.items():
                lines = striker.wrap_text(value, 90)
                for line in lines:
                    result += striker.get_line_align_left2(key, line) + "\n"
                    # print(f"${{goto 30}}${{alignc}}${{font4}}${{color red}}{line}")

            return result
        else:
            result = ""
            result += get_line(30, "", "Spectral Types", "")
            result += get_line(400, "", "Luminosity Classes", "") + f"\n"

            result += get_line(30, "Type", "Temp (K)", "Color")
            result += get_line(400, "Class", "Symbol", "Description") + f"\n"
            result += f"${{goto 30}}${{color gray}}${{hr 1}}" + f"\n"

            result += f"${{color blue}}" + get_line(30, "0", "> 30,000", "Blue")
            result += (
                f"${{color white}}" + get_line(400, "I", "I", "Supergiant") + f"\n"
            )

            result += f"${{color #aabfff}}" + get_line(
                30, "B", "10,000 - 30,000", "Blue-white"
            )

            result += (
                f"${{color white}}" + get_line(400, "II", "II", "Bright Giant") + f"\n"
            )

            result += f"${{color white}}" + get_line(
                30, "A", " 7,500 - 10,000", "White"
            )
            result += f"${{color white}}" + get_line(400, "III", "III", "Giant") + f"\n"

            result += f"${{color #ffffe0}}" + get_line(
                30, "F", " 6,000 -  7,500", "Yellow-white"
            )
            result += (
                f"${{color white}}" + get_line(400, "IV", "IV", "Sub-giant") + f"\n"
            )

            result += f"${{color yellow}}" + get_line(
                30, "G", " 5,200 -  6,000", "Yellow"
            )
            result += (
                f"${{color white}}"
                + get_line(400, "V", "V", "Main Sequence (Dwarf)")
                + f"\n"
            )

            result += f"${{color orange}}" + get_line(
                30, "K", " 3,700 -  5,200", "Orange"
            )
            result += (
                f"${{color white}}" + get_line(400, "VI", "VI", "Sub-dwarf") + f"\n"
            )

            result += f"${{color red}}" + get_line(30, "M", "< 3,700 ", "Red")
            result += (
                f"${{color white}}"
                + get_line(400, "D", "D", "White-dwarf (Dead core)")
                + f"\n"
            )

            return result
    except FileNotFoundError:
        raise exception.StrikerException(f"File not found: {FILE_NAME}")
    except PermissionError:
        raise exception.StrikerException(f"Permission denied: {FILE_NAME}")
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

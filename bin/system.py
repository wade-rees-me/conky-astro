#!/usr/bin/env python3

import striker
import exception


#
#
#
def get_system():
    results = f"${{font}}"
    results += (
        striker.get_line_align_right(
            f"OS | Kernel",
            f"${{texeci 3600 lsb_release -d  | awk '{{$1=\"\"; print $0}}'}} running on Kernel ${{kernel}}",
        )
        + f"\n"
    )
    results += striker.get_line_align_right(
        f"Uptime | Processes",
        f"${{color green}}${{uptime}}${{color}} with ${{color green}}${{processes}}${{color}} processes running",
    )
    return results


#
#
#
if __name__ == "__main__":
    print(striker.get_section_title("System", "${nodename}"))
    try:
        print(get_system())
    except exception.StrikerException as e:
        print(exception.StrikerException.get_message(e))

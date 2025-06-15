#!/usr/bin/env python3

import striker
import exception


#
#
#
def get_network():
    results = f"${{font}}"
    results += (
        striker.get_line_align_right(
            f"Public (NordVPN: 86.38.51.194) | Local | Gateway",
            f'${{if_match "${{exec curl -s ifconfig.me}}" != "86.38.51.194"}}${{color red}}'
            f"${{else}}${{color green}}${{endif}}${{exec curl -s ifconfig.me}} | "
            f"${{exec hostname -I | awk '{{print $1}}'}} | "
            f"${{exec ip route | awk '/default/ {{print $3}}'}}",
        )
        + f"\n"
    )
    results += striker.get_line_align_right(
        f"Total(speed) Download | Upload",
        f"${{alignr}}${{totaldown eno0}}(${{downspeed eno0}}) | ${{totalup eno0}}(${{upspeed eno0}})",
    )
    return results


#
#
#
if __name__ == "__main__":
    print(striker.get_section_title("Network", ""))
    try:
        print(get_network())
    except exception.StrikerException as e:
        print(exception.StrikerException.get_message(e))

#!/usr/bin/env python3

import striker
import exception


#
# get_system()
# Returns formatted system information for Conky, including OS, kernel, uptime, and process count.
#
def get_system():
    results = "${font}"

    # OS and kernel details
    os_info = "${texeci 3600 lsb_release -d | awk '{$1=\"\"; print $0}'} running on Kernel ${kernel}"
    results += striker.get_line_align_right("OS | Kernel", os_info) + "\n"

    # Uptime and processes
    uptime_info = "${color green}${uptime}${color} with ${color green}${processes}${color} processes running"
    results += striker.get_line_align_right("Uptime | Processes", uptime_info)

    return results


#
# Main Execution
#
if __name__ == "__main__":
    # Print section header with hostname
    print(striker.get_section_title("System", "${nodename}"))

    # Print system info or handle errors gracefully
    try:
        print(get_system())
    except exception.StrikerException as e:
        print(exception.StrikerException.get_message(e))

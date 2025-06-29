#!/usr/bin/env python3

import striker
import exception
import socket
import psutil
import time


#
#
#
def get_net_io(interface):
    stats1 = psutil.net_io_counters(pernic=True)[interface]
    time.sleep(1)
    stats2 = psutil.net_io_counters(pernic=True)[interface]

    total_down = stats2.bytes_recv
    total_up = stats2.bytes_sent
    down_speed = stats2.bytes_recv - stats1.bytes_recv
    up_speed = stats2.bytes_sent - stats1.bytes_sent

    return {
        "total_down": total_down,
        "total_up": total_up,
        "down_speed": down_speed,
        "up_speed": up_speed,
    }


#
#
#
def is_connected(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


#
#
#
def get_network():
    iface = "nordlynx"
    data = get_net_io(iface)
    total_down = data["total_down"] / striker.CONVERT_GB
    down_speed = data["down_speed"] / 1024
    total_up = data["total_up"] / striker.CONVERT_GB
    up_speed = data["up_speed"] / 1024

    results = "${font}"
    results += striker.get_line_align_right(
        ("Public (NordVPN: ${color green}86.38.51.194${color cyan}) | Local | Gateway"),
        (
            '${if_match "${exec curl -s ifconfig.me}" != "86.38.51.194"}${color red}'
            + "${else}${color green}${endif}"
            + "${exec curl -s ifconfig.me} | "
            + "${exec hostname -I | awk '{print $1}'} | "
            + "${exec ip route | awk '/default/ {print $3}'}"
            + " | ${color green}Connected\n"
            if is_connected()
            else "${color red}Disconnected\n"
        ),
    )
    results += striker.get_line_align_right(
        "Total transferred(speed)",
        f"${{alignr}}Download: {total_down:8,.1f} GB ({down_speed:8,.1f} KB/s) | Upload: {total_up:8,.1f} GB ({up_speed:8,.1f} KB/s)",
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

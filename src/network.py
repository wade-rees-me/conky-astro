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

    # Fetch the public IP using curl
    public_ip_from_curl = "${execi 1800 curl -s ifconfig.me}"
    public_ip = "${execi 1800 curl -s ifconfig.me}"
    local_ip = "${exec hostname -I | awk '{print $1}'}"
    gateway = "${exec ip route | awk '/default/ {print $3}'}"

    # Check internet connectivity
    connection_status = (
        "${color green}Connected" if is_connected() else "${color red}Disconnected"
    )

    # Create the formatted results string
    results = (
        striker.get_line_align_right(
            f"Public (${{color green}}{striker.CONKY_PUBLIC_IP}${{color cyan}})",
            f"Public: ${{color green}}{public_ip} | Local: {local_ip} | Gateway: {gateway} | {connection_status}",
        )
        + "\n"
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

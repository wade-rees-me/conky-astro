#!/usr/bin/env python3

import psutil
import striker
import exception

mountpoints = [
    "/",
    "/home",
    "/mnt/synology/volume1",
    "/mnt/synology/volume2",
    "/mnt/synology/volume3",
]


#
#
#
def get_disk_usage():
    results = f"${{font}}"

    i = 1
    for mountpoint in mountpoints:
        usage = psutil.disk_usage(mountpoint)
        disk_color = striker.get_color_percent(usage.percent)
        total = usage.total / striker.CONVERT_GB
        used = usage.used / striker.CONVERT_GB
        free = total - used
        size = f"Size: {total:>5,.0f} GB"
        free = f"Free: {free:>5,.0f} GB"
        used = f"Used: {used:>5,.0f} GB ({usage.percent:3.0f}%)"
        results += striker.get_line_align_right(
            f"{mountpoint}", f"${{color {disk_color}}}{size} | {free} | {used}"
        )
        if i < len(mountpoints):
            results += f"\n"
        i = i + 1
    return results


#
#
#
if __name__ == "__main__":
    print(striker.get_section_title("Disks", ""))
    try:
        print(get_disk_usage())
    except exception.StrikerException as e:
        print(exception.StrikerException.get_message(e))

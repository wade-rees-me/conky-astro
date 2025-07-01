#!/usr/bin/env python3

import psutil
import striker
import exception
import os


# Function to read mount points from a file
def read_mount_points(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


#
#
#
def get_disk_usage():
    results = f"${{font}}"
    mountpoints_file = os.path.join(striker.CONKY_ASTRO_DATA, "mountpoints.txt")
    mountpoints = read_mount_points(mountpoints_file)

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

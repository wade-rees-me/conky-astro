#!/usr/bin/env python3

import striker
import exception

# import argparse
import psutil

# import platform
import time
import subprocess


#
#
#
def get_cpu_model():
    try:
        result = subprocess.run(["lscpu"], capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            if "Model name" in line:
                return line.split(":")[1].strip()
    except Exception as e:
        return f"Error retrieving CPU model: {e}"


#
#
#
def conky_cpu_usage():
    # Get CPU and temperature info
    cpu_freq = psutil.cpu_freq()
    cpu_count_physical = psutil.cpu_count(logical=False)
    cpu_count_logical = psutil.cpu_count(logical=True)
    cpu_usage = psutil.cpu_percent(interval=1, percpu=False)
    cpu_usages = psutil.cpu_percent(interval=1, percpu=True)
    cpu_slices = [cpu_usages[i : i + 8] for i in range(0, len(cpu_usages), 8)]

    temps = psutil.sensors_temperatures()
    cpu_temps = [
        t.current for t in temps.get("coretemp", []) if t.label.startswith("Core ")
    ]
    overall_temp = sum(cpu_temps) / len(cpu_temps) if cpu_temps else 0.0

    lines = []
    lines.append(
        f"${{font}}${{goto 20}}${{color cyan}}Frequency: ${{alignr}}${{color white}}Min: {cpu_freq.min:.0f} MHz | "
        f"Max: {cpu_freq.max:.0f} MHz | Current: {cpu_freq.current:.0f} MHz"
    )
    lines.append(
        f"${{goto 20}}${{color cyan}}Cores: (temperatures in °C)${{alignr}}${{color white}}Physical: {cpu_count_physical} (0-23)"
        f"| Logical: {cpu_count_logical} | Usage: {cpu_usage:.0f}% | ${{color}}Temperature: {overall_temp:.0f}°C${{voffset 6}}"
    )

    for i, slice in enumerate(cpu_slices, start=0):
        output = f"${{goto 40}}${{color cyan}}{i*8:>2} - {(i+1)*8-1:>2}: ${{alignc}}"
        for j, usage in enumerate(slice, start=0):
            core_index = i * len(slice) + j
            temp = cpu_temps[core_index] if core_index < len(cpu_temps) else 0.0
            color = striker.get_color_percent(usage)
            if core_index < len(cpu_temps):
                temp = cpu_temps[core_index]
                t_color = striker.get_color_percent(temp)
                temp_display = f"${{color {t_color}}}{temp:2.0f}°"
            else:
                temp_display = "${color grey}---"
            output += f"${{color {color}}}{usage:>7.0f}%/{temp_display}"
        lines.append(output)

    return "\n".join(lines)


#
#
#
if __name__ == "__main__":
    print(striker.get_section_title("CPU", get_cpu_model()))
    try:
        print(conky_cpu_usage())
    except exception.StrikerException as e:
        print(exception.StrikerException.get_message(e))

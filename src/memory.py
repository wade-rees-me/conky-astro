#!/usr/bin/env python3

import psutil
import striker
import exception


#
#
#
def get_memory_usage():
    results = f"${{font}}"

    memory = psutil.virtual_memory()
    memory_size = memory.total / striker.CONVERT_GB
    memory_used = memory.used / striker.CONVERT_GB
    memory_free = memory_size - memory_used
    memory_percent = (memory.used / memory.total) * 100
    memory_color = striker.get_color_percent(memory_percent)

    swap = psutil.swap_memory()
    swap_size = swap.total / striker.CONVERT_GB
    swap_used = swap.used / striker.CONVERT_GB
    swap_free = swap_size - swap_used
    swap_percent = (swap.used / swap.total) * 100
    swap_color = striker.get_color_percent(swap_percent)

    results += (
        striker.get_line_align_right(
            f"Memory",
            f"${{color {memory_color}}}Size: {memory_size:>5,.0f} GB | Free: {memory_free:>5,.0f} GB | Used: {memory_used:>5,.0f} GB ({memory_percent:3.0f}%)",
        )
        + f"\n"
    )
    results += striker.get_line_align_right(
        f"Swap",
        f"${{color {swap_color}}}Size: {swap_size:>5,.0f} GB | Free: {swap_free:>5,.0f} GB | Used: {swap_used:>5,.0f} GB ({swap_percent:3.0f}%)",
    )
    return results


#
#
#
if __name__ == "__main__":
    print(striker.get_section_title("Memory", ""))
    try:
        print(get_memory_usage())
    except exception.StrikerException as e:
        print(exception.StrikerException.get_message(e))

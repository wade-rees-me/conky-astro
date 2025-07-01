#!/usr/bin/env python3

import GPUtil
import striker
import exception


#
#
#
def conky_gpu_model():
    gpus = GPUtil.getGPUs()
    for gpu in gpus:
        return gpu.name
    return ""


#
#
#
def conky_gpu_usage():
    results = f"${{font}}"

    gpus = GPUtil.getGPUs()
    for gpu in gpus:
        percent = gpu.memoryUsed / gpu.memoryTotal * 100
        color = striker.get_color_percent(percent)
        size = f"Size: {gpu.memoryTotal:>5,.0f} MB"
        free = f"Free: {gpu.memoryFree :>5,.0f} MB"
        used = f"Used: {gpu.memoryUsed :>5,.0f} MB ({percent:3.0f}%)"
        results += (
            f"${{goto 20}}${{color cyan}}Memory${{alignr}}${{color white}}{size} | {free} | {used}"
        ) + f"\n"
        results += (
            f"${{goto 20}}${{color cyan}}Metrics${{alignr}}${{color {color}}}Load: {gpu.load * 100:,.0f}% | ${{color white}}Temperature:"
            f"{gpu.temperature:,.0f}°C"
        )
        return results


#
#
#
if __name__ == "__main__":
    print(striker.get_section_title("GPU", conky_gpu_model()))
    try:
        print(conky_gpu_usage())
    except exception.StrikerException as e:
        print(exception.StrikerException.get_message(e))

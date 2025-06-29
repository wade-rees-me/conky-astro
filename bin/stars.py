#!/usr/bin/env python3

import striker
import json
import exception
import re

# from astroquery.simbad import Simbad
# from astropy.coordinates import SkyCoord, EarthLocation, AltAz
# import astropy.units as u
from datetime import date
import random
import os


#
#
#
def get_stars():
    star_data = striker.load_json(striker.FILE_STAR_DATA)
    star_items = [(name, data) for name, data in star_data.items() if name != "Sun"]

    # Load current index
    try:
        with open(striker.FILE_STAR_TOGGLE, "r") as f:
            index = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        index = 0

    # Rotate and get 6 items
    total = len(star_items)
    if total == 0:
        return
    index %= total
    rotated = star_items[index:] + star_items[:index]
    selected = rotated[:8]

    # Save updated index for next run
    next_index = (index + 1) % total
    with open(striker.FILE_STAR_TOGGLE, "w") as f:
        f.write(str(next_index))

    today_str = date.today().isoformat()  # e.g., '2025-06-22'
    lines = []

    for star_name, details in selected:
        luminosity = details.get("luminosity", 0)
        mass = details.get("mass_msun", 0)
        mag = details.get("app_mag", 0)
        spt = details.get("spectral_type", "---")
        spt_info = striker.parse_spectral_type(spt)

        # Use today's az/alt if available in daily_positions
        daily_positions = details.get("daily_positions", {})
        today_position = daily_positions.get(today_str, {})
        az = today_position.get("azimuth_deg", 0.0)
        alt = today_position.get("altitude_deg", 0.0)

        constellation = details.get("constellation", "Unknown")
        meaning = details.get("meaning", "Unknown")
        distance = details.get("distance_ly", 0)

        color = "green" if alt > 0 else "lightgray"

        line = (
            f"${{goto 20}}${{font}}${{color cyan}}{star_name:<12.12}"
            f"${{alignr}}| {constellation:<15} | {meaning:<17} | "
            f"${{color {spt_info['color_code']}}}{spt_info['color']:<13} | "
            f"{spt_info['size']:<13}"
            f"${{color {color}}} | {az:03.0f}° | {alt:+03.0f}° | "
            f"{distance:9,.1f} ly | {mass:>7.2f} MS"
        )
        lines.append(line)

    return "\n".join(lines)


#
#
#
if __name__ == "__main__":
    print(striker.get_section_title("Stars", ""))
    print(
        f"${{color yellow}}${{goto 20}}Star${{alignr}}| Constellation   | Meaning           | Temperature   | Star type     | Az   | Alt  | Distance     | Mass      "
    )
    print(f"${{goto 10}}${{voffset -8}}${{color gray}}${{hr 1}}${{voffset -5}}")
    try:
        print(get_stars())
    except exception.StrikerException as e:
        print(exception.StrikerException.get_message(e))

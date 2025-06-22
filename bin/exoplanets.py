#!/usr/bin/env python3

from astropy.coordinates import SkyCoord, AltAz
from astropy.time import Time
from astropy import units as u
from datetime import datetime, timedelta
import os
import json
import striker
import exception

DISPLAY_COUNT = 8


def get_rotation_index(total):
    """Read the rotation index from file, increment, and return it."""
    try:
        with open(striker.FILE_EXOPLANET_TOGGLE, "r") as f:
            index = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        index = 0

    new_index = (index + 1) % total
    with open(striker.FILE_EXOPLANET_TOGGLE, "w") as f:
        f.write(str(new_index))
    return index


def get_exoplanets():
    today = datetime.utcnow().date()
    obstime = Time.now()
    altaz_frame = AltAz(obstime=obstime, location=striker.UTAH_HERRIMAN)
    exoplanet_data = striker.load_json(striker.FILE_EXOPLANET_DATA)
    exoplanets = list(exoplanet_data.items())
    total = len(exoplanets)

    # Rotation index for display paging
    start_index = get_rotation_index(total)
    visible = exoplanets[start_index:] + exoplanets[:start_index]
    visible = visible[:DISPLAY_COUNT]

    lines = []
    for exoplanet, data in visible:
        try:
            mass = data.get("mass_earth", 0)
            distance = data.get("star_distance_ly", 0)
            world_type = data.get("world_type", "")
            exo_type = data.get("type", "")
            host_star = data.get("host_star", "")
            star_type = data.get("star_spectral_type", "")
            spt_info = striker.parse_spectral_type(star_type)

            obs = next(
                (o for o in data["observations"] if o["date"] == today.isoformat()),
                None,
            )
            color = "lightgray"
            if obs:
                az = obs["azimuth_deg"]
                alt = obs["altitude_deg"]
                color = "green" if alt > 0 else "lightgray"
            else:
                az = "---"
                alt = "---"

            line = (
                f"${{goto 20}}${{color cyan}}{exoplanet[:18]}${{alignr}}"
                f"${{color {color}}}| {host_star[:18]:<18} | "
                f"${{color {spt_info['color_code']}}}{spt_info['color']:<13} | "
                f"{spt_info['size']:<13}${{color {color}}} | {world_type:<13}"
                f"${{color {color}}} | "
                f"{az:03.0f}° | {alt:+03.0f}° | "
                f"{distance:>9,.2f} ly | {mass:>7.2f} Me"
            )
            lines.append(line)
        except Exception as e:
            lines.append(f"${{goto 20}}${{color red}}Error: {exoplanet} – {str(e)}")

    return "\n".join(lines)


if __name__ == "__main__":
    print(
        f"${{color yellow}}${{goto 20}}Exoplanet${{alignr}}| Host star          | Temperature   | Star type     | World Type    | Az   | Alt  | Distance     | Mass      "
    )
    print(f"${{goto 10}}${{voffset -8}}${{color gray}}${{hr 1}}${{voffset -5}}")
    try:
        print(get_exoplanets())
    except exception.StrikerException as e:
        print(exception.StrikerException.get_message(e))

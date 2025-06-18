#!/usr/bin/env python3

from astropy.coordinates import get_body, SkyCoord, AltAz, EarthLocation
from astropy.time import Time
from datetime import datetime
from astropy import units as u
import os
import json
import striker
import exception

DISPLAY_COUNT = 9


#
#
#
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


#
#
def get_exoplanets():
    obstime = Time.now()
    altaz_frame = AltAz(obstime=obstime, location=striker.herriman)

    exoplanet_data = striker.load_json(striker.FILE_EXOPLANET_DATA)
    exoplanets = list(exoplanet_data.items())
    total = len(exoplanets)

    # Get current rotation index
    start_index = get_rotation_index(total)
    rotated = exoplanets[start_index:] + exoplanets[:start_index]
    visible = rotated[:DISPLAY_COUNT]

    lines = []

    for exoplanet, data in visible:
        mass = data["mass_earths"]
        distance = data["distance_ly"]
        ra_str = data["ra"]
        dec_str = data["dec"]
        exo_type = data["type"]
        host_star = data["host_star"]
        star_type = data["star_type"]
        spt_info = striker.parse_spectral_type(star_type)

        coord = SkyCoord(ra=ra_str, dec=dec_str, frame="icrs")
        altaz = coord.transform_to(altaz_frame)
        color = "green" if altaz.alt > 0 else "lightgray"

        line = (
            f"${{goto 40}}${{color cyan}}{exoplanet}${{alignr}}"
            f"${{color {color}}}| {host_star:<26} | {spt_info['type']}-{spt_info['size']:<4} | {exo_type:<14} | "
            f"{altaz.az.value:03.0f}° | {altaz.alt.value:+03.0f}° | "
            f"{distance:>9,.2f} ly | {mass:>6.2f} Me"
        )
        lines.append(line)

    return "\n".join(lines)


#
#
#
if __name__ == "__main__":
    # print(striker.get_section_title("Exoplanets", ""))
    # print(f"\n")
    print(
        f"${{color yellow}}${{goto 30}}Exoplanet${{alignr}}| Host star                  | SpT    | World Type     | Az   | Alt  | Distance     | Mass     "
    )
    print(f"${{goto 30}}${{voffset -8}}${{color gray}}${{hr 1}}${{voffset -5}}")
    try:
        print(get_exoplanets())
    except exception.StrikerException as e:
        print(exception.StrikerException.get_message(e))

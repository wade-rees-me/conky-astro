#!/usr/bin/env python3

from astropy.coordinates import get_body, AltAz, EarthLocation
from astropy.time import Time
from datetime import datetime
from astropy import units as u
import os
import json
import striker
import exception


#
#
#
def get_planets():
    objstime = Time.now()
    planet_data = striker.load_json(striker.FILE_PLANET_DATA)
    lines = []

    for planet_name, details in planet_data.items():
        mass = details.get("mass_earths")
        planet_type = details.get("type")
        distance = details.get("distance_au")
        magnitude = details.get("magnitude")
        temp_k = details.get("avg_temp_k")
        temp_f = striker.kelvin_to_fahrenheit(temp_k)
        radius_miles = striker.kilometers_to_miles(details.get("radius_km"))

        body = get_body(planet_name, objstime, location=striker.herriman)
        altaz = body.transform_to(AltAz(obstime=objstime, location=striker.herriman))

        alt = altaz.alt.deg
        az = altaz.az.deg
        color = "green" if alt > 0 else "lightgray"

        if planet_name == "Earth":
            line = (
                f"${{goto 40}}${{color cyan}}{planet_name}${{alignr}}${{color {color}}}| {radius_miles:>10,.0f} mi | {temp_f:>+8.0f}°F | {magnitude:+06.2f}"
                f" | {planet_type:<14} | ---- | ---- | ------------ | {mass:>6.2f} Me"
            )
        else:
            line = (
                f"${{goto 40}}${{color cyan}}{planet_name}${{alignr}}${{color {color}}}| {radius_miles:>10,.0f} mi | {temp_f:>+8.0f}°F | {magnitude:+06.2f}"
                f" | {planet_type:<14} | {az:03.0f}° | {alt:+03.0f}° | {distance:>9,.2f} AU | {mass:>6.2f} Me"
            )
        lines.append(line)

    return "\n".join(lines)


#
#
#
if __name__ == "__main__":
    print(striker.get_section_title("Planets", ""))
    print(
        f"${{color yellow}}${{goto 30}}Planet${{alignr}}| Radius        | Temp       | Mag    | World Type     | Az   | Alt  | Distance     | Mass     "
    )
    print(f"${{goto 30}}${{voffset -8}}${{color gray}}${{hr 1}}${{voffset -5}}")
    try:
        print(get_planets() + f"\n")
    except exception.StrikerException as e:
        print(exception.StrikerException.get_message(e))

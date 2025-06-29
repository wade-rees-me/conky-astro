#!/usr/bin/env python3

from datetime import datetime
import os
import json
import striker
import exception


#
#
#
def get_planets():
    today = datetime.utcnow().date().isoformat()

    planet_data = striker.load_json(striker.FILE_PLANET_DATA)
    solar_data = striker.load_json(striker.FILE_SOLAR_SYSTEM_DATA)
    today_data = solar_data.get(today, {})
    planet_positions = today_data.get("planets", {})

    lines = []

    for planet_name, details in planet_data.items():
        mass = details.get("mass_earths")
        planet_type = details.get("type")
        distance = details.get("distance_au")
        magnitude = details.get("magnitude")
        orbit_days = details.get("orbit_days")
        rotation_period_hours = details.get("rotation_period_hours")
        temp_k = details.get("avg_temp_k")
        temp_f = striker.kelvin_to_fahrenheit(temp_k)
        radius_miles = striker.kilometers_to_miles(details.get("radius_km"))

        # Get position info from solar system data JSON
        pos = planet_positions.get(planet_name.lower(), {})
        az = pos.get("azimuth_deg")
        alt = pos.get("altitude_deg")

        if az is not None and alt is not None:
            color = "green" if alt > 0 else "lightgray"
            az_str = f"{az:03.0f}°"
            alt_str = f"{alt:+03.0f}°"
        else:
            color = "lightgray"
            az_str = "----"
            alt_str = "----"

        cleaned = planet_name.replace(" barycenter", "")
        if cleaned == "earth":
            line = (
                f"${{goto 20}}${{color cyan}}{cleaned.title()}${{alignr}}${{color {color}}}| {rotation_period_hours:>8,.0f} h | {orbit_days:>6,.0f} d | {radius_miles:>6,.0f} mi | {temp_f:>+4.0f}°F | {magnitude:+06.2f}"
                f" | {planet_type:<13} | ---- | ---- | ------------ | {mass:>7.2f} Me"
            )
        else:
            line = (
                f"${{goto 20}}${{color cyan}}{cleaned.title()}${{alignr}}${{color {color}}}| {rotation_period_hours:>8,.0f} h | {orbit_days:>6,.0f} d | {radius_miles:>6,.0f} mi | {temp_f:>+4.0f}°F | {magnitude:+06.2f}"
                f" | {planet_type:<13} | {az_str} | {alt_str} | {distance:>9,.2f} AU | {mass:>7.2f} Me"
            )

        lines.append(line)

    return "\n".join(lines)


#
#
#
if __name__ == "__main__":
    print(striker.get_section_title("Planets", ""))
    print(
        f"${{color yellow}}${{goto 20}}Planet${{alignr}}| Rotation   | Orbit    | Radius    | Temp   | Mag    | World Type    | Az   | Alt  | Distance     | Mass      "
    )
    print(f"${{goto 10}}${{voffset -8}}${{color gray}}${{hr 1}}${{voffset -5}}")
    try:
        print(get_planets() + f"\n")
    except exception.StrikerException as e:
        print(exception.StrikerException.get_message(e))

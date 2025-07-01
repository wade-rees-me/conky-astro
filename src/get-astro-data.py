#!/usr/bin/env python3

import os
import striker
import json
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from skyfield.api import load, Topos, load_file
from skyfield.almanac import find_discrete, sunrise_sunset, risings_and_settings

LOCATION = Topos(latitude_degrees=40.7, longitude_degrees=-111.9)  # Salt Lake City
PLANETS = [
    "mercury",
    "venus",
    "earth",
    "mars",
    "jupiter barycenter",
    "saturn barycenter",
    "uranus barycenter",
    "neptune barycenter",
]

SUN_LABELS = {0: "sunset", 1: "sunrise"}
MOON_LABELS = {0: "moonset", 1: "moonrise"}


def get_phase_info(angle):
    if angle < 22.5 or angle >= 337.5:
        return ("new_moon", "🌑")
    elif angle < 67.5:
        return ("waxing_crescent", "🌒")
    elif angle < 112.5:
        return ("first_quarter", "🌓")
    elif angle < 157.5:
        return ("waxing_gibbous", "🌔")
    elif angle < 202.5:
        return ("full_moon", "🌕")
    elif angle < 247.5:
        return ("waning_gibbous", "🌖")
    elif angle < 292.5:
        return ("last_quarter", "🌗")
    elif angle < 337.5:
        return ("waning_crescent", "🌘")


def group_events_by_date(times, events, labels):
    grouped = defaultdict(dict)
    for t, e in zip(times, events):
        date = t.utc_datetime().date().isoformat()
        label = labels[e]
        grouped[date][label] = t.utc_strftime("%H:%M")
    return grouped


def ensure_ephemeris():
    if not os.path.exists(striker.FILE_EPH_DATA):
        eph = load("de422.bsp")
        os.rename(eph.filename, striker.FILE_EPH_DATA)
    return load_file(striker.FILE_EPH_DATA)


def collect_data():
    eph = ensure_ephemeris()
    ts = load.timescale()
    observer = eph["earth"] + LOCATION

    today = datetime.utcnow().date()
    start = ts.utc(today.year, today.month, today.day)
    end = ts.utc(today.year, today.month, today.day + 90)

    sun_times, sun_events = find_discrete(start, end, sunrise_sunset(eph, LOCATION))
    moon_times, moon_events = find_discrete(
        start, end, risings_and_settings(eph, eph["moon"], LOCATION)
    )

    sun_data = group_events_by_date(sun_times, sun_events, SUN_LABELS)
    moon_data = group_events_by_date(moon_times, moon_events, MOON_LABELS)

    daily_data = defaultdict(dict)
    for date in set(list(sun_data.keys()) + list(moon_data.keys())):
        daily_data[date].update(sun_data.get(date, {}))
        daily_data[date].update(moon_data.get(date, {}))

    current = today
    while current <= (today + timedelta(days=90)):
        date_str = current.isoformat()
        t = ts.utc(current.year, current.month, current.day)

        sun_pos = observer.at(t).observe(eph["sun"]).apparent()
        moon_pos = observer.at(t).observe(eph["moon"]).apparent()

        phase_angle = sun_pos.separation_from(moon_pos).degrees
        illumination = (1 + np.cos(np.radians(phase_angle))) / 2 * 100
        phase_name, emoji = get_phase_info(phase_angle)

        _, sun_dec, _ = sun_pos.radec()
        sun_declination = round(sun_dec.degrees, 4)

        sunrise = daily_data[date_str].get("sunrise")
        sunset = daily_data[date_str].get("sunset")
        day_length = "--:--"
        if sunrise and sunset:
            try:
                sr = datetime.strptime(sunrise, "%H:%M")
                ss = datetime.strptime(sunset, "%H:%M")
                delta = ss - sr
                if delta.total_seconds() < 0:
                    delta += timedelta(days=1)
                hours, rem = divmod(delta.total_seconds(), 3600)
                minutes = int(rem // 60)
                day_length = f"{int(hours)}:{minutes:02d}"
            except Exception:
                pass

        daily_data[date_str].update(
            {
                "moon_illumination_percent": round(illumination, 1),
                "sun_declination": sun_declination,
                "day_length": day_length,
                "moon_phase": phase_name,
                "moon_emoji": emoji,
            }
        )

        planets_info = {}
        for planet_name in PLANETS:
            planet = eph[planet_name]
            app = observer.at(t).observe(planet).apparent()

            alt, az, distance = app.altaz()
            ra, dec, _ = app.radec()
            dist_au = distance.au

            planets_info[planet_name] = {
                "azimuth_deg": round(az.degrees, 2),
                "altitude_deg": round(alt.degrees, 2),
                "right_ascension_hr": round(ra.hours, 3),
                "declination_deg": round(dec.degrees, 3),
                # "distance_au": round(dist_au, 5),
            }

        daily_data[date_str]["planets"] = planets_info
        current += timedelta(days=1)

    with open(striker.FILE_SOLAR_SYSTEM_DATA, "w") as f:
        json.dump(daily_data, f, indent=2)

    print(f"✅ 3-month solar system data written to: {striker.FILE_SOLAR_SYSTEM_DATA}")


if __name__ == "__main__":
    collect_data()

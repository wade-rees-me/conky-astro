#!/usr/bin/env python3

import striker
import random
import os
import json
from datetime import datetime, timedelta
from astroquery.utils.tap.core import TapPlus
from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from astropy.time import Time
from astropy import units as u
import numpy.ma as ma
import math

# Location for Az/Alt calculations (Salt Lake City, UT)
location = EarthLocation(lat=40.7 * u.deg, lon=-111.9 * u.deg, height=1500 * u.m)


def classify_world_type(mass_earth):
    """Return world type based on approximate Earth-mass ranges."""
    if mass_earth is None:
        return "Unknown"
    if mass_earth < 2:
        return "Terrestrial"
    elif mass_earth < 10:
        return "Super-Earth"
    elif mass_earth < 50:
        return "Mini-Neptune"
    elif mass_earth < 100:
        return "Ice Giant"
    else:
        return "Gas Giant"


def get_safe(val, default=None, ndigits=None):
    """Safely return float values, accounting for masked or None."""
    if val is None or val is ma.masked:
        return default
    try:
        v = float(val)
        return round(v, ndigits) if ndigits is not None else v
    except Exception:
        return default


def luminosity_relative_to_sun(radius_rsun, temp_k):
    """Return luminosity as multiple of solar luminosity (L☉)."""
    if radius_rsun is None or temp_k is None:
        return None
    try:
        return (radius_rsun**2) * ((temp_k / 5778) ** 4)
    except Exception:
        return None


def apparent_brightness_lsun(luminosity_lsun, distance_pc):
    """Return apparent brightness approximation (arbitrary units)."""
    if luminosity_lsun is None or distance_pc is None or distance_pc == 0:
        return None
    return round(luminosity_lsun / (4 * math.pi * distance_pc**2), 6)


# TAP query: fetch 1000 nearest exoplanets
tap = TapPlus(url="https://exoplanetarchive.ipac.caltech.edu/TAP")
query = """
SELECT TOP 1000
    pl_name, pl_bmassj, pl_bmasse, pl_orbsmax, ra, dec, hostname,
    st_teff, st_rad, st_mass, sy_dist, st_spectype
FROM pscomppars
WHERE pl_bmasse IS NOT NULL AND sy_dist IS NOT NULL AND st_spectype IS NOT NULL
ORDER BY sy_dist ASC
"""

# tap = TapPlus(url="https://exoplanetarchive.ipac.caltech.edu/TAP")
job = tap.launch_job(query)
table = job.get_results()

# Shuffle & select 36 random exoplanets
rows = list(table)
random.shuffle(rows)
selected = rows[:36]
exoplanet_data = {}

# Build 90-day observation window
today = datetime.utcnow().date()
dates = [today + timedelta(days=i) for i in range(90)]

# for row in table:
for row in selected:
    pl_name = row["pl_name"]
    coord = SkyCoord(ra=row["ra"] * u.deg, dec=row["dec"] * u.deg)
    host_star = row["hostname"]
    mass_jup = get_safe(row["pl_bmassj"], ndigits=4)
    mass_earth = get_safe(row["pl_bmasse"], ndigits=2)
    orbital_distance = get_safe(row["pl_orbsmax"], ndigits=4)
    temp_k = get_safe(row["st_teff"])
    radius_rsun = get_safe(row["st_rad"])
    mass_msun = get_safe(row["st_mass"])
    distance_pc = get_safe(row["sy_dist"], ndigits=2)
    world_type = classify_world_type(mass_earth)
    distance_ly = round(distance_pc * 3.26156, 2) if distance_pc else None
    spectral_type = (
        row["st_spectype"]
        if row["st_spectype"] and not ma.is_masked(row["st_spectype"])
        else None
    )

    # Estimate luminosity & apparent brightness
    lum_lsun = luminosity_relative_to_sun(radius_rsun, temp_k)
    app_brightness = apparent_brightness_lsun(lum_lsun, distance_pc)

    world = {
        "host_star": host_star,
        "mass_jupiter": mass_jup,
        "mass_earth": mass_earth,
        "world_type": world_type,
        "orbital_distance_au": orbital_distance,
        "star_temp_K": temp_k,
        "star_radius_Rsun": radius_rsun,
        "star_mass_Msun": mass_msun,
        "star_distance_pc": distance_pc,
        "star_distance_ly": distance_ly,
        "star_spectral_type": spectral_type,
        "observations": [],
    }

    for dt in dates:
        time = Time(dt.isoformat() + " 00:00:00")
        altaz = coord.transform_to(AltAz(obstime=time, location=location))
        world["observations"].append(
            {
                "date": dt.isoformat(),
                "azimuth_deg": round(altaz.az.deg, 2),
                "altitude_deg": round(altaz.alt.deg, 2),
            }
        )

    exoplanet_data[pl_name] = world

# Sort by distance (parsecs)
sorted_data = dict(
    sorted(exoplanet_data.items(), key=lambda kv: kv[1]["star_distance_pc"] or 9999)
)

with open(striker.FILE_EXOPLANET_DATA, "w") as f:
    json.dump(sorted_data, f, indent=2)

print(f"✅ Exoplanet data for 90 days written to: {striker.FILE_EXOPLANET_DATA}")

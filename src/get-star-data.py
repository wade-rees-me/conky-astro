#!/usr/bin/env python3

import json
import striker
from datetime import datetime, timedelta
from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from astropy.time import Time
from astropy import units as u
from astroquery.simbad import Simbad
import warnings

warnings.filterwarnings("ignore")

# Brightest stars per northern constellation (name, full constellation)
brightest_stars = [
    ("Polaris", "Ursa Minor", "Lesser Bear"),
    ("Alioth", "Ursa Major", "Great Bear"),
    ("Schedar", "Cassiopeia", "Ethiopia Queen"),
    ("Alderamin", "Cepheus", "Ethiopia King"),
    ("Deneb", "Cygnus", "Swan"),
    ("Vega", "Lyra", "Lyre (Harp)"),
    ("Alpheratz", "Andromeda", "Ethiopia Princess"),
    ("Mirfak", "Perseus", "Slayer of Medusa"),
    ("Capella", "Auriga", "Charioteer"),
    ("Eltanin", "Draco", "Dragon"),
    ("Kornephoros", "Hercules", "Hercules"),
    ("Arcturus", "Boötes", "Herdsman"),
    ("Alphecca", "Corona Borealis", "Northern Crown"),
    ("Rotanev", "Delphinus", "Dolphin"),
    ("Anser", "Vulpecula", "Little Fox"),
    ("Sham", "Sagitta", "Arrow"),
    ("Altair", "Aquila", "Eagle"),
    ("Kitalpha", "Equuleus", "Little Horse"),
]

# Observer location and times
location = EarthLocation(lat=40.5142 * u.deg, lon=-112.0325 * u.deg, height=1500 * u.m)
now = datetime.utcnow()
dates = [now + timedelta(days=i) for i in range(90)]

# Configure Simbad to include required fields
Simbad.reset_votable_fields()
Simbad.add_votable_fields("ra", "dec", "flux(V)", "sp", "plx")


results = {}

# Query each star
for star_name, constellation, meaning in brightest_stars:
    try:
        result = Simbad.query_object(star_name)
        if result is None:
            print(f"❌ Not found: {star_name}")
            continue

        ra = result["ra"][0]
        dec = result["dec"][0]
        mag = float(result["V"][0]) if result["V"].mask is False else None
        sp_type = result["sp_type"][0]
        plx = result["plx_value"][0]
        distance_pc = 1000.0 / plx if plx and plx > 0 else None
        distance_ly = round(distance_pc * 3.26156, 2) if distance_pc else None

        coord = SkyCoord(ra=ra, dec=dec, unit=(u.hourangle, u.deg))

        daily = {}
        for dt in dates:
            t = Time(dt)
            altaz = coord.transform_to(AltAz(obstime=t, location=location))
            daily[dt.strftime("%Y-%m-%d")] = {
                "azimuth_deg": round(altaz.az.deg, 2),
                "altitude_deg": round(altaz.alt.deg, 2),
            }

        results[star_name] = {
            "constellation": constellation,
            "meaning": meaning,
            "spectral_type": sp_type,
            "visual_mag": mag,
            "distance_ly": distance_ly,
            "coordinates": {"ra": ra, "dec": dec},
            "daily_positions": daily,
        }

        print(f"✅ {star_name} ({constellation})")
    except Exception as e:
        print(f"❌ Error with {star_name}: {e}")

# Save to JSON
with open(striker.FILE_STAR_DATA, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Star data saved to {striker.FILE_STAR_DATA}")

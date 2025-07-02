#!/usr/bin/env python3

from astropy.coordinates import EarthLocation
from astropy import units as u
import math
import json
import re
import os


# Earth's radius in miles
EARTH_RADIUS_MI = 3958.8

#
CONVERT_GB = 1024**3

# Load and convert latitude and longitude from environment variables
try:
    CONKY_LOCAL_IP = os.getenv("CONKY_LOCAL_IP")
    CONKY_PUBLIC_IP = os.getenv("CONKY_PUBLIC_IP")

    KEY_OPEN_WEATHER_API = os.getenv("KEY_OPEN_WEATHER_API")

    CONKY_HOME = os.environ.get("CONKY_HOME", "/home/wade/Conky")
    CONKY_ASTRO_HOME = os.getenv("CONKY_ASTRO_HOME")
    CONKY_AIRPORT_CODE = os.getenv("CONKY_AIRPORT_CODE", "KSLC")
except ValueError as e:
    raise ValueError(f"Invalid environment variables: {e}")

#
CONKY_ASTRO_SCRIPTS = os.path.join(CONKY_ASTRO_HOME, "scripts")
CONKY_ASTRO_DATA = os.path.join(CONKY_ASTRO_HOME, "data")
CONKY_ASTRO_CACHE = os.path.join(CONKY_ASTRO_HOME, "cache")

#
# add constants
#
FILE_EPH_DATA = os.path.join(CONKY_ASTRO_CACHE, "de422.bsp")
FILE_AIRPORT_DATA = os.path.join(CONKY_ASTRO_DATA, "airport-data.json")
FILE_DEFINITION_DATA = os.path.join(CONKY_ASTRO_DATA, "definitions.json")
FILE_DEFINITION_TOGGLE = os.path.join(CONKY_ASTRO_CACHE, "definition-toggle.txt")

FILE_SOLAR_SYSTEM_DATA = os.path.join(CONKY_ASTRO_CACHE, "solar-system-data.json")
FILE_EXOPLANET_DATA = os.path.join(CONKY_ASTRO_CACHE, "exoplanet-data.json")
FILE_EXOPLANET_TOGGLE = os.path.join(CONKY_ASTRO_CACHE, "exoplanet-toggle.txt")
FILE_PLANET_DATA = os.path.join(CONKY_ASTRO_DATA, "planet-data.json")
FILE_STAR_DATA = os.path.join(CONKY_ASTRO_CACHE, "star-data.json")
FILE_STAR_TOGGLE = os.path.join(CONKY_ASTRO_CACHE, "star-toggle.txt")


#
#
#
def wrap_text(text, max_width=120):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + (1 if current_line else 0) <= max_width:
            current_line += (" " if current_line else "") + word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


#
# Function to determine color
#
def get_color_percent(value):
    if value == 0:
        return "white"
    if value > 80:
        return "red"
    if value > 60:
        return "yellow"
    return "green"


#
# Load pre-cached star data from JSON
#
def load_json(filename):
    with open(filename, "r") as file:
        return json.load(file)


#
#
#
def parse_spectral_type(spt):
    # Spectral class → (Color, Temp in Kelvin, Color Code)
    spectral_classes = {
        "O": ("Blue", 40000, "blue"),
        "B": ("Blue-White", 20000, "lightblue"),
        "A": ("White", 8500, "white"),
        "F": ("Yellow-White", 6500, "lightyellow"),
        "G": ("Yellow", 5800, "yellow"),
        "K": ("Orange", 4500, "orange"),
        "M": ("Red", 3200, "red"),
    }

    luminosity_classesX = {
        "I": "I",
        "II": "II",
        "III": "III",
        "IV": "IV",
        "V": "V",
        "VI": "VI",
        "VII": "VII",
    }
    luminosity_classes = {
        "I": "Supergiant",
        "II": "Bright Giant",
        "III": "Giant",
        "IV": "Sub-giant",
        "V": "Main Sequence",
        "VI": "Sub-dwarf",
        "VII": "White-dwarf",
    }

    if not spt:
        return {
            "type": "-",
            "color": "-",
            "temperature": "-",
            "size": "-",
            "color_code": "gray",
        }

    match = re.match(r"([OBAFGKM])(\d)?([IV]+)?", spt)
    if not match:
        return {
            "type": "-",
            "color": "-",
            "temperature": "-",
            "size": "-",
            "color_code": "gray",
        }

    spectral_class = match.group(1)
    subclass = int(match.group(2)) if match.group(2) else 5
    lum_class_raw = match.group(3) or "V"

    # Get color and base temp
    color, base_temp, color_code = spectral_classes.get(
        spectral_class, ("Unknown", 0, "gray")
    )
    # Adjust temp slightly by subclass (lower subclass = hotter)
    temp = int(base_temp - (subclass * (base_temp * 0.05)))

    # Map luminosity class
    size = luminosity_classes.get(lum_class_raw, "Unknown")

    return {
        "type": spectral_class,
        "color": color,
        "temperature": temp,
        "size": size,
        "color_code": color_code,
    }


def classify_luminosity_class(spectral):
    if not spectral:
        return "?"
    if "Ia" in spectral or "Ib" in spectral:
        return "🌟"  # Supergiant
    elif "III" in spectral:
        return "🌕"  # Giant
    elif "IV" in spectral:
        return "🌓"  # Subgiant
    elif "V" in spectral:
        return "☀️"  # Main sequence
    elif "D" in spectral:
        return "⚪"  # White dwarf
    return "?"


def classify_temp_color(temp_k):
    if temp_k is None:
        return ("?", "?")
    t = float(temp_k)
    if t >= 30000:
        return ("Blue", "🔵")
    elif t >= 10000:
        return ("Blue-white", "🔹")
    elif t >= 7500:
        return ("White", "⚪")
    elif t >= 6000:
        return ("Yellow-white", "🟡")
    elif t >= 5000:
        return ("Yellow", "🟨")
    elif t >= 3500:
        return ("Orange", "🟧")
    else:
        return ("Red", "🔴")


#
#
#
def get_section_title(label, tag):
    return f"${{goto 10}}${{color yellow}}${{font3}}{label} {tag} ${{hr 2}}${{font}}"


#
#
#
def get_line_align_left(label, data):
    return f"${{goto 20}}${{color cyan}}${{font}}{label}:${{goto 140}}${{color white}}{data}"


def get_line_align_left2(label, data):
    return f"${{goto 20}}${{color cyan}}${{font}}{label}:${{goto 180}}${{color white}}{data}"


#
#
#
def get_line_align_right(label, data):
    return (
        f"${{goto 20}}${{color cyan}}${{font}}{label}${{alignr}}${{color white}}{data}"
    )


#
#
#
def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance between two lat/lon pairs in miles."""
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_MI * c


#
#
#
def initial_bearing(lat1, lon1, lat2, lon2):
    """Calculate initial bearing from point 1 to point 2 in degrees."""
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon_rad = math.radians(lon2 - lon1)

    x = math.sin(dlon_rad) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(
        lat2_rad
    ) * math.cos(dlon_rad)

    bearing_rad = math.atan2(x, y)
    bearing_deg = math.degrees(bearing_rad)
    return (bearing_deg + 360) % 360  # Normalize to 0–360 degrees


#
#
#
def azimuth_direction(az_deg):
    """Convert azimuth degrees to compass direction."""
    directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    index = int((az_deg + 11.25) % 360 // 22.5)
    return directions[index]


#
#
#
def altitude_description(alt_deg):
    """Categorize altitude angle into visibility height."""
    if alt_deg < 0:
        return "Below"
    elif alt_deg < 20:
        return "Low"
    elif alt_deg < 50:
        return "Mid"
    else:
        return "High"


#
#
#
def location_description(az, alt):
    direction = azimuth_direction(az)
    height = altitude_description(alt)
    return f"{height:<5}, {direction:>3}"


#
#
#
def celsius_to_fahrenheit(celsius):
    return (celsius * 9 / 5) + 32


#
# Convert Kelvin to Fahrenheit.
#
def kelvin_to_fahrenheit(kelvin):
    return (kelvin - 273.15) * 9 / 5 + 32


#
#
#
def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5 / 9


#
#
#
def dew_point_celsius(temp_celsius, humidity_percent):
    a = 17.62
    b = 243.12
    gamma = (a * temp_celsius) / (b + temp_celsius) + math.log(humidity_percent / 100.0)
    dew_point = (b * gamma) / (a - gamma)
    return dew_point


#
#
#
def hectopascals_to_inches_of_mercury(hectopascals):
    return hectopascals * 0.02953


#
#
#
def meters_per_second_to_miles_per_hour(meters_per_second):
    return meters_per_second * 2.23694


#
# Convert kilometers to miles.
#
def kilometers_to_miles(km):
    return km * 0.621371


#
#
#
def meters_to_miles(meters):
    return meters / 1609.344


#
#
#
def meters_to_feet(meters):
    return meters * 3.28084


#
#
#
def millimeters_to_inches(millimeters):
    return millimeters / 25.4

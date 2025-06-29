#!/usr/bin/env python3
"""
Display current weather data for a rotating set of airports including KSLC,
using OpenWeatherMap and formatting for Conky.
"""

import json
import os
import time
import requests
import pytz
from datetime import datetime
from astropy.coordinates import EarthLocation
import striker
import exception

# Rotate through different airports every 3 minutes
ROTATION_INTERVAL_SECONDS = 3 * 60


# --- Helper Functions ---


def get_current_airports(airport_coords, n=4):
    """
    Return a rotating selection of 'n' airport codes (excluding KSLC)
    based on the current time interval.
    """
    rotating_keys = [key for key in airport_coords if key != "KSLC"]
    now = time.time()
    base_index = int(now // ROTATION_INTERVAL_SECONDS) % len(rotating_keys)
    return [
        (
            rotating_keys[(base_index + i) % len(rotating_keys)],
            airport_coords[rotating_keys[(base_index + i) % len(rotating_keys)]],
        )
        for i in range(n)
    ]


def get_weather(lat, lon, api_key):
    """
    Query the OpenWeatherMap API for current weather at a given latitude and longitude.
    """
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"lat={lat}&lon={lon}&appid={api_key}&units=metric"
    )
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch weather: {response.status_code} {response.text}"
        )
    return response.json()


def get_temp_color(temp_f):
    if temp_f < 35:
        return "color2"
    elif temp_f < 55 or temp_f > 80:
        return "color yellow"
    elif temp_f > 90:
        return "color violet"
    return "color green"


def get_pressure_color(pressure_inhg):
    if pressure_inhg < 29.80:
        return "color2"
    elif pressure_inhg > 30.20:
        return "color green"
    return "color yellow"


def calculate_heat_index(temp_f, humidity):
    if temp_f < 80 or humidity < 40:
        return temp_f
    # Simplified Steadman's formula
    return temp_f + 0.33 * humidity - 0.7


def calculate_wind_chill(temp_f, wind_mph):
    if temp_f > 50 or wind_mph < 3:
        return temp_f
    return (
        35.74
        + 0.6215 * temp_f
        - 35.75 * (wind_mph**0.16)
        + 0.4275 * temp_f * (wind_mph**0.16)
    )


def calculate_density_altitude(elevation_ft, temp_c, pressure_inhg):
    isa_temp_c = 15.0 - (elevation_ft / 1000.0) * 2.0
    da = elevation_ft + 118.8 * (temp_c - isa_temp_c) + 118.8 * (29.92 - pressure_inhg)
    return da


def display_weather(code, info, data, is_kslc):
    name = info.get("name")
    location = info.get("location")
    elevation_m = info.get("elevation_m")
    elevation_ft = striker.meters_to_feet(elevation_m)
    distance = info.get("distance_from_KSLC_miles")
    direction = info.get("direction_from_KSLC_degrees")

    main = data["main"]
    wind = data.get("wind", {})
    rain = data.get("rain", {})
    snow = data.get("snow", {})
    weather = data["weather"][0]

    # Convert values
    temp_c = main["temp"]
    temp_f = striker.celsius_to_fahrenheit(temp_c)
    humidity = main["humidity"]
    pressure = main["pressure"]
    wind_speed_mps = wind.get("speed", 0)
    wind_speed_mph = striker.meters_per_second_to_miles_per_hour(wind_speed_mps)
    wind_dir = wind.get("deg", "N/A")
    visibility_m = data.get("visibility", None)

    # Derived values
    dew_c = striker.dew_point_celsius(temp_c, humidity)
    dew_f = striker.celsius_to_fahrenheit(dew_c)
    pressure_inhg = striker.hectopascals_to_inches_of_mercury(pressure)
    heat_index = calculate_heat_index(temp_f, humidity)
    wind_chill = calculate_wind_chill(temp_f, wind_speed_mph)
    density_alt = calculate_density_altitude(
        info.get("elevation_ft", 4300), temp_c, pressure_inhg
    )

    # Colors
    temp_color = get_temp_color(temp_f)
    pressure_color = get_pressure_color(pressure_inhg)

    # Precipitation
    precipitation = "dry"
    if rain:
        mm = rain.get("1h", rain.get("3h", 0))
        precipitation = f"{striker.millimeters_to_inches(mm):.1f} inches of rain"
    elif snow:
        mm = snow.get("1h", snow.get("3h", 0))
        precipitation = f"{striker.millimeters_to_inches(mm):.1f} inches of snow"

    # Visibility
    visibility_str = ""
    if visibility_m is not None:
        visibility_str = f"{striker.meters_to_miles(visibility_m):.1f} miles"

    # Header
    if is_kslc:
        print(
            f"${{goto 10}}${{color yellow}}${{font3}}{name} - {location} ({code}) ${{hr 2}}${{font}}"
        )
    else:
        print(
            f"${{goto 10}}${{color yellow}}${{font3}}{name} - {location} "
            f"({code}, {distance:.0f} miles at {direction:.0f}°) ${{hr 2}}${{font}}"
        )

    # Body
    print(
        f"${{goto 20}}${{color cyan}}Temperature | Dew Point | Humidity | Pressure${{alignr}}"
        f"${{{temp_color}}}{temp_c:.0f}°C ({temp_f:.0f}°F) | "
        f"${{color white}}{dew_c:.0f}°C ({dew_f:.0f}°F) | {humidity}% | "
        f"${{{pressure_color}}}{pressure_inhg:.2f} inHg"
    )
    print(
        f"${{goto 20}}${{color cyan}}Heat Index | Wind Chill | Density Altitude | Elevation${{alignr}}"
        f"${{color white}}{heat_index:.0f}°F | {wind_chill:.0f}°F | {density_alt:.0f} ft | {elevation_ft:.0f} ft"
    )
    print(
        f"${{goto 20}}${{color cyan}}Conditions${{alignr}}${{color white}}"
        f"{wind_speed_mph:.0f} mph from {wind_dir}°, {precipitation} with {visibility_str} visibility"
    )
    print(
        f"${{goto 20}}${{color cyan}}Sky (clouds)${{alignr}}${{color white}}{weather['description'].title()}"
    )


def go_weather(code, info, is_kslc):
    lat = info["latitude"]
    lon = info["longitude"]
    weather_data = get_weather(lat, lon, striker.KEY_OPEN_WEATHER_API)
    display_weather(code, info, weather_data, is_kslc)


def get_kslc_data(airport_coords):
    return airport_coords.get("KSLC")


# --- Main Execution ---
if __name__ == "__main__":
    try:
        airport_coords = striker.load_json(striker.FILE_AIRPORT_DATA)

        # Show KSLC first
        kslc_info = get_kslc_data(airport_coords)
        go_weather("KSLC", kslc_info, True)

        # Show other rotating airports
        rotating_airports = get_current_airports(airport_coords)
        for code, info in rotating_airports:
            go_weather(code, info, False)

    except exception.StrikerException as e:
        print(exception.StrikerException.get_message(e))
    except Exception as e:
        print(f"${{color red}}Error: {e}")

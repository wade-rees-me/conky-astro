#!/usr/bin/env python3

import json
import striker
import exception
from datetime import datetime
import time
import requests
import pytz
import os

# OPENWEATHER_API_KEY = "79764014333bc411583aa941ea6817ba"
ROTATION_INTERVAL_SECONDS = 3 * 60


#
#
#
def get_current_airports(airport_coords, n=3):
    rotating_airport_keys = [key for key in airport_coords.keys() if key != "KSLC"]
    now = time.time()
    base_index = int(now // ROTATION_INTERVAL_SECONDS) % len(rotating_airport_keys)
    return [
        (
            rotating_airport_keys[(base_index + i) % len(rotating_airport_keys)],
            airport_coords[
                rotating_airport_keys[(base_index + i) % len(rotating_airport_keys)]
            ],
        )
        for i in range(n)
    ]


#
#
#
def get_weather(lat, lon, api_key):
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


#
#
#
def display_weather(code, info, data, slc):
    name = info["name"]
    location = info["location"]
    distance_from = info["distance_from_KSLC_miles"]
    direction_from = info["direction_from_KSLC_degrees"]

    main = data["main"]
    wind = data.get("wind", {})
    rain = data.get("rain", {})
    snow = data.get("snow", {})
    weather = data["weather"][0]

    temp_c = main["temp"]
    temp_f = striker.celsius_to_fahrenheit(temp_c)
    temp_color = "color green"
    if temp_f < 55:
        temp_color = "color yellow"
    elif temp_f < 35:
        temp_color = "color2"
    elif temp_f > 80:
        temp_color = "color yellow"
    elif temp_f > 90:
        temp_color = "color violet"

    humidity = main["humidity"]
    pressure = main["pressure"]
    visibility_m = data.get("visibility", None)
    wind_speed_mps = wind.get("speed", 0)
    wind_speed_mph = striker.meters_per_second_to_miles_per_hour(wind_speed_mps)
    wind_dir = wind.get("deg", "N/A")
    visibility_final = ""
    rain_total = ""
    snow_total = ""
    precipitation = "dry"
    dew_c = striker.dew_point_celsius(temp_c, humidity)
    dew_f = dew_c * 9 / 5 + 32
    pressure_inhg = striker.hectopascals_to_inches_of_mercury(pressure)
    pressure_color = "color yellow"
    if pressure_inhg < 29.80:
        pressure_color = "color2"
    if pressure_inhg > 30.20:
        pressure_color = "color green"

    if visibility_m is not None:
        visibility_miles = striker.meters_to_miles(visibility_m)
        visibility_final = f"{visibility_miles:.1f} miles"

    if rain:
        rain_mm = rain.get("1h", rain.get("3h", 0))
        precipitation = f"{striker.millimeters_to_inches(rain_mm):.1f} inches of rain"

    if snow:
        snow_mm = snow.get("1h", snow.get("3h", 0))
        precipitation = f"{striker.millimeters_to_inches(snow_mm):.1f} inches of snow"

    if slc:
        print(
            f"${{goto 20}}${{color yellow}}${{font3}}{name} - {location} ({code}) ${{hr 2}}${{font}}"
        )
    else:
        print(
            f"${{goto 20}}${{color yellow}}${{font3}}{name} - {location} ({code}, {distance_from:.0f} miles at {direction_from:.0f}°) ${{hr 2}}${{font}}"
        )
    print(
        f"${{goto 30}}${{color cyan}}Temperature | Dew Point | Humidity | Pressure: ${{alignr}}${{{temp_color}}}{temp_c:.0f}°C ({temp_f:.0f}°F) | "
        f"${{color white}}{dew_c:.0f}°C ({dew_f:.0f}°F) | {humidity}% | "
        f"${{{pressure_color}}}{pressure_inhg:.2f} inHg"
    )
    print(
        f"${{goto 30}}${{color cyan}}Conditions: ${{alignr}}${{color white}}{wind_speed_mph:.0f} mph from {wind_dir}°, "
        f"{precipitation} with {visibility_final} visibility"
    )
    print(
        f"${{goto 30}}${{color cyan}}Sky (clouds): ${{alignr}}${{color white}}{weather['description'].title()}"
    )


#
#
#
def go_weather(code, info, slc):
    lat = info["latitude"]
    lon = info["longitude"]
    weather_data = get_weather(lat, lon, striker.OPENWEATHER_API_KEY)
    display_weather(code, info, weather_data, slc)


#
#
#
def load_airport_coords(filename):
    with open(filename, "r") as file:
        return json.load(file)


#
#
#
def get_kslc_data(airport_coords):
    return airport_coords.get("KSLC", None)


#
#
#
if __name__ == "__main__":
    airport_coords = load_airport_coords(striker.FILE_AIRPORT_DATA)

    kslc_info = get_kslc_data(airport_coords)  # Create rotation list excluding KSLC
    go_weather("KSLC", kslc_info, True)

    current_airports = get_current_airports(airport_coords)
    for code, info in current_airports:
        go_weather(code, info, False)

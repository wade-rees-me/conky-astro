#!/usr/bin/env python3

import striker
import exception
import os
import requests
from datetime import datetime
from datetime import date

# Load environment variables
# API_KEY = "143feb9467a64e01aff65746d10081f9"
# LAT = "37.258"
# LON = "-122"


#
#
#
def get_sun_and_moon():
    # Fetch astronomy data
    DATE = date.today().isoformat()
    url = f"https://api.ipgeolocation.io/astronomy?apiKey={striker.API_KEY}&lat={striker.LAT}&long={striker.LON}"
    response = requests.get(url)

    # Check for HTTP errors
    if response.status_code != 200:
        try:
            error_json = response.json()
            message = error_json.get("message", "Unknown error")
        except ValueError:
            message = "Invalid JSON response"

        lines = striker.wrap_text(message, 120)

        print(
            f"${{goto 30}}${{alignc}}${{font4}}${{color white}}Request failed with status code {response.status_code}"
        )
        for line in lines:
            print(f"${{goto 30}}${{alignc}}${{font4}}${{color red}}{line}")
        return

    try:
        sunrise_ampm = "--:--"
        sunset_ampm = "--:--"
        day_length = "--.--"
        astro_data = response.json()
        # print("Astronomy data:", astro_data)
        # Extract data
        sunrise = astro_data["sunrise"]  # e.g., "05:47"
        sunset = astro_data["sunset"]  # e.g., "17:58"
        day_length = astro_data["day_length"]

        # Convert to datetime with corrected format
        sunrise_dt = datetime.strptime(f"{DATE} {sunrise}", "%Y-%m-%d %H:%M")
        sunset_dt = datetime.strptime(f"{DATE} {sunset}", "%Y-%m-%d %H:%M")

        sunrise_ampm = sunrise_dt.strftime("%I:%M %p")
        sunset_ampm = sunset_dt.strftime("%I:%M %p")

        moonrise = "--:--"
        moonset = "--:--"
        moon_phase = "-----"
        illumination = "-----"

        # Fetch moon data from the API
        moon_data = response.json()

        # Extract moonrise, moonset, and moon phase
        moonrise = moon_data.get("moonrise")
        moonset = moon_data.get("moonset")
        moon_phase = moon_data.get("moon_phase").replace("_", " ").capitalize()
        illumination = moon_data.get("moon_illumination_percentage")

    except ValueError:
        print("Error: Response was not valid JSON.")

    # Output the result
    print(
        f"${{goto 30}}${{alignc}}${{font4}}${{color white}}Sunrise: {sunrise_ampm} | Sunset: {sunset_ampm} | Day length: {day_length} hours"
    )
    print(
        f"${{goto 30}}${{alignc}}${{font4}}${{color white}}{moon_phase} moon | Moonrise: {moonrise} | Moonset: {moonset} | Illumination: {illumination}%"
    )


#
#
#
if __name__ == "__main__":
    try:
        get_sun_and_moon()
    except exception.StrikerException as e:
        print(exception.StrikerException.get_message(e))

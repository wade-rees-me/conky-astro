#!/usr/bin/env python3


#
#
#
def add_distance_and_direction(airports, reference_key="KSLC"):
    kslc = airports[reference_key]
    kslc_lat = kslc["latitude"]
    kslc_lon = kslc["longitude"]
    for code, data in airports.items():
        lat = data["latitude"]
        lon = data["longitude"]
        distance = striker.haversine_distance(kslc_lat, kslc_lon, lat, lon)
        bearing = striker.initial_bearing(kslc_lat, kslc_lon, lat, lon)
        data["distance_from_KSLC_miles"] = round(distance, 1)
        data["direction_from_KSLC_degrees"] = round(bearing, 1)
    return airports

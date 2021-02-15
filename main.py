"""
This module contains functions to find the films filmed nearby.
"""
import sys
import string
import logging

import imdb
import folium
import numpy as np
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

DEBUG = False

# configure logging
if not DEBUG:
    logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
else:
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def prepare_location_title_data(data_file: str='locations.list') -> dict:
    """
    This function reads file's lines & processes them.
    Returns a dict with title-location pair.
    """

    def process_location(location: str):
        """
        This subfunction processes location.
        """
        wo_description = location.strip(" \n").split('(')[0]
        # if location is exact enough
        if wo_description.count(',') >= 2:
            return wo_description.translate(
                str.maketrans('', '', string.punctuation)
            )
        return None

    logging.debug(f"Reading {data_file}...")
    lines = np.array(open(data_file, 'rb').readlines())

    # skip the header
    logging.debug("Skipping the header...")
    start_ind = 0
    for line_i, line in enumerate(lines):
        if line == b'==============\n':
            start_ind = line_i + 1
            break
    lines = lines[start_ind:]

    location_title_dict = dict()

    logging.debug("Processing file...")
    for line in lines:
        try:
            title_location = line.decode("utf-8").split("\t")
        except UnicodeDecodeError:
            pass
        title = imdb.utils.analyze_title(title_location[0])['title']
        location = process_location("".join(title_location[1:]))
        if location is not None:
            location_title_dict.setdefault(location, []).append(title)

    return location_title_dict


def find_closest_locations(
        current_user_location: str, location_title_dict: dict
    ) -> np.array:
    """
    This function finds closest matches to a string in a keys of a dictionary.
    """
    matching_locations_dict = dict()
    user_location_tags = list(reversed(current_user_location.split(", ")))
    for file_location in location_title_dict.keys():
        file_location_tags = list(reversed(file_location.split(" ")))
        for user_tag_num, user_tag in enumerate(user_location_tags):
            if user_tag.isnumeric():
                continue
            # input(f"{user_tag = }\n{file_location_tags = }")
            if user_tag in file_location_tags:
                if file_location in matching_locations_dict:
                    matching_locations_dict[file_location] += user_tag_num
                else:
                    matching_locations_dict[file_location] = user_tag_num

    best_matches = np.array(list(map(
        lambda x: x[0],
        sorted(
            list(matching_locations_dict.items()),
            key=lambda x: -x[1]
        )
    )))

    return best_matches


def generate_html(
        location, geocode,
        latitude: float=49.817545, longitude: float=24.023932, html_path="map.html"
    ):
    """
    This function generatess and html file containing a map with films.
    """
    page_map = folium.Map(
        titles="OpenStreetMap",
        location=[latitude, longitude],
        zoom_start=10
    )

    location_title_dict = prepare_location_title_data()

    current_user_location = location.address
    logging.debug(f"{current_user_location = }")

    logging.debug("Finding current closest films...")
    best_matches = find_closest_locations(current_user_location, location_title_dict)

    logging.debug("Finding current closest films locations...")
    closest_films_featuregroup = folium.FeatureGroup(name="Closest films")
    films_num_left = 20
    for match in best_matches:
        match_location = geocode(match)
        if match_location is None:
            continue
        match_lat, match_lon = match_location.latitude, match_location.longitude

        closest_films_featuregroup.add_child(folium.Marker(
            location=[match_lat, match_lon],
            popup=folium.Popup(folium.Html(
                ", ".join(location_title_dict[match])
            ), min_width=500, max_width=500),
            icon=folium.Icon()
        ))

        films_num_left -= 1
        if films_num_left <= 0:
            break

    page_map.add_child(closest_films_featuregroup)

    user_location_featuregroup = folium.FeatureGroup(name="Your location")
    user_location_featuregroup.add_child(folium.Marker(
        location=[latitude, longitude],
        popup=folium.Popup(folium.Html(
            "Your Location"
        ), min_width=100, max_width=100),
        icon=folium.Icon(color="red")
    ))
    page_map.add_child(user_location_featuregroup)

    page_map.save(html_path)


def main():
    """
    An interactive function of the module.
    """
    geolocator = Nominatim(user_agent="Closest films locator.")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    ans = input("Do you want to find your location by name? (Y/n): ")
    if ans in ["y", "Y", ""]:
        loc_str = input("Enter your current location in English: ")
        match = geocode(loc_str)
        if match is not None:
            latitude, longitude = match.latitude, match.longitude
        else:
            print("Error while finding your location.")
            latitude = float(input("Please enter your current latitude: "))
            longitude = float(input("Please enter your current longitude: "))
    else:
        latitude = float(input("Please enter your current latitude: "))
        longitude = float(input("Please enter your current longitude: "))

    location = geolocator.reverse(f"{latitude}, {longitude}", language='en')

    map_html_name = 'map.html'
    print("Generating the map, please wait...")
    generate_html(
        location, geocode,
        latitude=latitude, longitude=longitude,
        html_path=map_html_name
    )
    print(f"Your map is saved in: {map_html_name}")


if __name__ == "__main__":
    main()

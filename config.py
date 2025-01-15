import json
import os

default_settings = {
    "space_maps": True,
    "starting_id": 4197,
    "accuracy": 100,
    "display_bad": False,
    "display_partial": True,
    "display_perfect": True
}

file_path = "settings.json"

if not os.path.exists(file_path):
    with open(file_path, "w") as file:
        json.dump(default_settings, file, indent=4)

with open(file_path, "r") as file:
    settings_json = json.load(file)

class Config:
    SPACE_MAPS = settings_json["space_maps"]           # Enable if you want to have an empty line between each map in the console
    STARTING_ID = settings_json["starting_id"]         # The Map ID to begin gathering information from. Note that ID 4197 is the 1st map, not ID 1
    ACCURACY = settings_json["accuracy"] / 100         # The accuracy to calculate the RP for (0-100)
    DISPLAY_BAD = settings_json["display_bad"]         # Whether or not you'd like to print the info of maps that do not match any of your desired conditions.
    DISPLAY_PARTIAL = settings_json["display_partial"] # Whether or not you'd like to print the info of maps that match a part of your desired conditions.
    DISPLAY_PERFECT = settings_json["display_perfect"] # Whether or not you'd like to print the info of maps that match the perfect condition.
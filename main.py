import colors
import conditions
import config

import requests
import os
import math

import random

os.system("cls")

Conditions = conditions.Conditions
Colors = colors.Colors
Config = config.Config

BEATMAP_PAGE_URL = "https://development.rhythia.com/api/getBeatmaps"
BEATMAP_PAGE_ID_URL = "https://development.rhythia.com/api/getBeatmapPageById" # for top plays
USER_SCORES_URL = "https://development.rhythia.com/api/getUserScores"

NEWLINE = "\n"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "MapList/1.0 (UID=10151)"
}

#----- RP CALC

def ease_in_expo_deq_hard(acc: float, star: float):
	exponent = 100 - 12 * star
	exponent = max(exponent, 5)
	return 0 if acc == 0 else math.pow(2, exponent * acc - exponent)

def calculate_rp(star: float, acc: float, speed: float):
    star *= speed
    eased_rp = (star * ease_in_expo_deq_hard(acc, star) * 100)
    final_rp = math.pow(eased_rp / 2, 2) / 1000

    rounded_rp = round(final_rp, 2)
    return rounded_rp * 2

#----- RP CALC

#----- HELPERS

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes}:{seconds:02}"

def create_scores_payload(user_id: int):
    return {"id": user_id, "session": "N/A1"}

def create_map_payload(map_id: str):
    return {"mapId": map_id, "session":"N/A1"}

def create_map_page_payload(min_stars: float, max_stars: float):
    return {"minStars": min_stars, "maxStars": max_stars, "status": "APPROVED", "session": "N/A1"}
    # there isnt enough ranked maps, so for now i will only be using legacy maps

#----- HELPERS


def process_map(beatmap):
    length = max(1, beatmap['length'] / 1000)
    # nps = beatmap['noteCount'] / length
    sr = beatmap['starRating']
    normal_rp = calculate_rp(sr, Config.ACCURACY, 1)
    speed4_rp = calculate_rp(sr, Config.ACCURACY, 1.45)

    is_perfect = Conditions.perfect_4(speed4_rp, length) or Conditions.perfect_0(normal_rp, length)
    is_partial = (
        Conditions.rp_0(normal_rp) or Conditions.rp_4(speed4_rp)
        or Conditions.star_rating(sr) or Conditions.length_0(length)
    )

    if is_perfect and Config.DISPLAY_PERFECT:
        print(f"{Colors.PERFECT}{beatmap['title']} | RP (1x): {normal_rp:.2f}, "
              f"RP (1.45x): {speed4_rp:.2f} | Length: {format_time(round(length))} | "
              f"Star Rating: {sr:.2f}*{Colors.RESET}{NEWLINE if Config.SPACE_MAPS else ''}")
    elif is_partial and Config.DISPLAY_PARTIAL:
        print(f"{Colors.RESET}{beatmap['title']} | "
              f"{Colors.GOOD_RP0 if Conditions.rp_0(normal_rp) else Colors.RESET}RP (1x): {normal_rp:.2f}{Colors.RESET}, "
              f"{Colors.GOOD_RP4 if Conditions.rp_4(speed4_rp) else Colors.RESET}RP (1.45x): {speed4_rp:.2f}{Colors.RESET} | "
              f"{Colors.GOOD_LENGTH if Conditions.length_0(length) else Colors.RESET}Length: {format_time(round(length))}{Colors.RESET} | "
              f"{Colors.GOOD_SR if Conditions.star_rating(sr) else Colors.RESET}Star Rating: {sr:.2f}*{Colors.RESET}{NEWLINE if Config.SPACE_MAPS else ''}")
    elif not is_partial and Config.DISPLAY_BAD:
        print(f"{Colors.RESET}{beatmap['title']} | RP (1x): {normal_rp:.2f}, RP (1.45x): {speed4_rp:.2f} | "
              f"Length: {format_time(round(length))} | Star Rating: {sr:.2f}*{Colors.RESET}{NEWLINE if Config.SPACE_MAPS else ''}")

def process_scores():
    scores_response = requests.post(USER_SCORES_URL, json=create_scores_payload(Config.USER_ID))
    data = scores_response.json()
    top_plays = data["top"]

    sr_list = []

    for i in top_plays:
        # beatmap_payload = {"session":"","mapId":i["songId"]}
        map_response = requests.post(BEATMAP_PAGE_ID_URL, json=create_map_payload(i["songId"]))

        map_data = map_response.json()["beatmap"]
        map_sr = map_data["starRating"]

        sr_list.append(map_sr)

    sr_list = sorted(sr_list, reverse=True)

    min_sr = sr_list[-1]
    max_sr = sr_list[0]

    return min_sr, max_sr

def main():
    min_sr, max_sr = process_scores()

    success = True
    map_index = 0 # will go up to 5

    print(str(min_sr) + " " + str(max_sr))

    while success:
        response = requests.post(BEATMAP_PAGE_URL, json=create_map_page_payload(min_sr, max_sr))
        try:
            response.raise_for_status()
            data = response.json()
            beatmaps = data["beatmaps"]
            while map_index < 5 and beatmaps:
                i = random.choice(beatmaps) # randomized to reduce repetition
                beatmaps.remove(i)

                process_map(i)
                map_index += 1
            else:
                success = False
                print(f"{Colors.ERROR}Exiting...{Colors.RESET}")
        except (requests.RequestException, ValueError) as e:
            success = False
            print(f"{Colors.ERROR}Error: {e}{Colors.RESET}")

if __name__ == "__main__":
    main()
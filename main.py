import colors
import conditions
import config

import requests
import os
import math

os.system("cls")

Conditions = conditions.Conditions
Colors = colors.Colors
Config = config.Config

URL = "https://development.rhythia.com/api/getBeatmapPage"

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
    
def create_payload(map_id: int):
    return {"id": map_id, "session": "N/A1"}
#----- HELPERS 

def process_map(beatmap):
    length = max(1, beatmap['length'] / 1000)
    nps = beatmap['noteCount'] / length
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
              f"Note Count: {beatmap['noteCount']} ({nps:.2f} NPS) | Star Rating: {sr:.2f}*{Colors.RESET}{NEWLINE if Config.SPACE_MAPS else ''}")
    elif is_partial and Config.DISPLAY_PARTIAL:
        print(f"{Colors.RESET}{beatmap['title']} | "
              f"{Colors.GOOD_RP0 if Conditions.rp_0(normal_rp) else Colors.RESET}RP (1x): {normal_rp:.2f}{Colors.RESET}, "
              f"{Colors.GOOD_RP4 if Conditions.rp_4(speed4_rp) else Colors.RESET}RP (1.45x): {speed4_rp:.2f}{Colors.RESET} | "
              f"{Colors.GOOD_LENGTH if Conditions.length_0(length) else Colors.RESET}Length: {format_time(round(length))}{Colors.RESET} | "
              f"Note Count: {beatmap['noteCount']} ({nps:.2f} NPS) | "
              f"{Colors.GOOD_SR if Conditions.star_rating(sr) else Colors.RESET}Star Rating: {sr:.2f}*{Colors.RESET}{NEWLINE if Config.SPACE_MAPS else ''}")
    elif not is_partial and Config.DISPLAY_BAD:
        print(f"{Colors.RESET}{beatmap['title']} | RP (1x): {normal_rp:.2f}, RP (1.45x): {speed4_rp:.2f} | "
              f"Length: {format_time(round(length))} | Note Count: {beatmap['noteCount']} ({nps:.2f} NPS) | Star Rating: {sr:.2f}*{Colors.RESET}{NEWLINE if Config.SPACE_MAPS else ''}")

def main():
    success = True
    current_id = Config.STARTING_ID

    while success:
        response = requests.post(URL, json=create_payload(current_id), headers=HEADERS)
        # print(response.json())5
        try:
            response.raise_for_status()
            data = response.json()
            if 'beatmap' in data:
                process_map(data['beatmap'])
                current_id += 1
            else:
                success = False
                print(f"{Colors.ERROR}No beatmap data found for ID {current_id}. Exiting...{Colors.RESET}")
        except (requests.RequestException, ValueError) as e:
            success = False
            print(f"{Colors.ERROR}Error: {e}{Colors.RESET}")

if __name__ == "__main__":
    main()
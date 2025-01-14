import requests
import os

os.system("cls")

#----- CONFIGURATION 
class Colors:
    ERROR = "\033[38;2;255;0;0m"         # Error color
    RESET = "\033[0m"                    # Default text color
    PERFECT = "\033[38;2;0;255;0m"       # The color that should be used when a map is perfect to your liking (full message color)
    GOOD_SR = "\033[38;2;255;255;0m"     # The color that should be used when a map has a good star rating
    GOOD_LENGTH = "\033[38;2;0;255;255m" # The color that should be used when a map's length is good
    GOOD_RP0 = "\033[38;2;255;0;255m"    # The color that should be used when a map awards good RP on normal speed
    GOOD_RP4 = "\033[38;2;0;0;255m"      # The color that should be used when a map awards good RP on normal speed++++ (1.45x)

class Conditions:
    star_rating = staticmethod(lambda sr: 3.72 < sr < 4.6)
    length_0 = staticmethod(lambda length: length < 62)
    length_4 = staticmethod(lambda length: length < 93)
    rp_0 = staticmethod(lambda rp: rp > 85)
    rp_4 = staticmethod(lambda rp: rp > 118)
    perfect_0 = staticmethod(lambda rp, length: rp > 85 and length < 60)
    perfect_4 = staticmethod(lambda rp, length: rp > 118 and length < 90)

class Config: 
    SPACE_MAPS = True       # Enable if you want to have an empty line between each map in the console  
    STARTING_ID = 4197      # The Map ID to begin gathering information from. Note that ID 4197 is the 1st map, not ID 1
    ACCURACY = 1            # The accuracy to calculate the RP for (0-1)
    DISPLAY_BAD = False     # Whether or not you'd like to print the info of maps that do not match any of your desired conditions.
    DISPLAY_PARTIAL = True # Whether or not you'd like to print the info of maps that match a part of your desired conditions.
    DISPLAY_PERFECT = True  # Whether or not you'd like to print the info of maps that match the perfect condition.
#----- CONFIGURATION

URL = "https://development.rhythia.com/api/getBeatmapPage"

NEWLINE = "\n"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "MapList/1.0 (UID=10151)"
}

#----- RP CALC 
def k(i):
    if 100 - 12 * i < 5:
        return 5
    else:
        return 100 - 12 * i
    
def f(x, s):
    return 2 ** (k(s) * x - k(s))
    
def p(s, a):
    return ((((s * f(a, s) * 100) / 2) ** 2) / 1000) * 2

def calculate_rp(s, a, m):
    return p(s * m, a)
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
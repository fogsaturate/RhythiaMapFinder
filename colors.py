class Colors:
    ERROR = "\033[38;2;255;0;0m"         # Error color
    RESET = "\033[0m"                    # Default text color
    PERFECT = "\033[38;2;0;255;0m"       # The color that should be used when a map is perfect to your liking (full message color)
    GOOD_SR = "\033[38;2;255;255;0m"     # The color that should be used when a map has a good star rating
    GOOD_LENGTH = "\033[38;2;0;255;255m" # The color that should be used when a map's length is good
    GOOD_RP0 = "\033[38;2;255;0;255m"    # The color that should be used when a map awards good RP on normal speed
    GOOD_RP4 = "\033[38;2;0;0;255m"      # The color that should be used when a map awards good RP on normal speed++++ (1.45x)
"""Constants for Vestel & Toshiba TV Remote Control integration."""

DOMAIN = "vestel_toshiba_tv"
DEFAULT_PORT = 56789
DIAL_APP_PATH = "/apps/SmartCenter"
SCAN_INTERVAL = 30  # seconds

# Key codes
KEY_CODES = {
    "power":        1012,
    "mute":         1013,
    "volume_up":    1016,
    "volume_down":  1017,
    "channel_up":   1032,
    "channel_down": 1033,
    "up":           1020,
    "down":         1019,
    "left":         1021,
    "right":        1022,
    "ok":           1053,
    "back":         1010,
    "home":         1048,
    "menu":         1066,
    "exit":         1037,
    "source":       1056,
    "internet":     1065,
    "favorites":    1062,
    "play":         1025,
    "stop":         1049,
    "channel_list": 1053,
    "0":            1000,
    "1":            1001,
    "2":            1002,
    "3":            1003,
    "4":            1004,
    "5":            1005,
    "6":            1006,
    "7":            1007,
    "8":            1008,
    "9":            1009,
}

SOURCE_LIST = ["HDMI 1", "HDMI 2", "HDMI 3", "AV", "PC", "TV", "YouTube", "Netflix"]

SOURCE_CODES = {
    "HDMI 1":  1056,
    "HDMI 2":  1056,
    "HDMI 3":  1056,
    "AV":      1056,
    "PC":      1056,
    "TV":      1056,
    "YouTube": 1065,
    "Netflix": 1065,
}

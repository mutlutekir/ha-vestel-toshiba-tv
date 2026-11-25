"""Constants for Vestel & Toshiba TV Remote Control integration."""

DOMAIN = "vestel_toshiba_tv"
DEFAULT_PORT = 56789
DIAL_APP_PATH = "/apps/SmartCenter"
SCAN_INTERVAL = 30  # seconds

# Options
# Sent when the options change; applied live (no reload, see __init__.py)
SIGNAL_OPTIONS_UPDATED = f"{DOMAIN}_options_updated_{{}}"
# Sent by the media player with its entity_id, for the sensors that follow it
SIGNAL_TV_ENTITY = f"{DOMAIN}_tv_entity_{{}}"
DATA_TV_ENTITY = "tv_entity_{}"
CONF_VOLUME_STEPS = "volume_steps"
DEFAULT_VOLUME_STEPS = 3
MIN_VOLUME_STEPS = 1
MAX_VOLUME_STEPS = 10

# Optional shortcut inputs for Apple Home / Siri. HomeKit gives Siri no
# volume or channel control for TVs, only switching inputs; these extra inputs
# run the action instead of switching input. Name per HA language ("tr",
# otherwise "en").
CONF_SHORTCUT_SOURCES = "shortcut_sources"
SHORTCUT_SOURCES = {
    "volume_up": {"en": "Volume up", "tr": "Ses artır"},
    "volume_down": {"en": "Volume down", "tr": "Ses azalt"},
    "channel_up": {"en": "Next channel", "tr": "Sonraki kanal"},
    "channel_down": {"en": "Previous channel", "tr": "Önceki kanal"},
}
VOLUME_KEYS = ("volume_up", "volume_down")
CHANNEL_KEYS = ("channel_up", "channel_down")

# The broadcast input: choosing it closes Netflix/YouTube
TV_SOURCE = "TV"

# After closing Netflix/YouTube via DIAL, give the broadcast this long to come
# back (seconds)
APP_CLOSE_DELAY = 3.0

# The TV's built-in DLNA renderer reports the real volume and mute state.
# It is read-only in practice (SetVolume does not reach the TV speaker), so
# the volume is changed with remote keys and read back from here.
DMR_PORT = 2870
DMR_CONTROL_PATH = "/RenderingControl/control"
# Rounds of "read volume, press keys" when setting an exact volume
VOLUME_SET_ROUNDS = 3

# The TV pushes events over a websocket. In normal standby the TV stays on the
# network (DIAL still says "running"); the only sign is "tv_status:1" here.
# "tv_state" events arrive when the TV is in use again.
WS_PORT = 7681
WS_RECONNECT_DELAY = 10  # seconds

# The power key is a toggle. After pressing it, wait this long for the TV's
# websocket answer (standby or awake); if the TV went the wrong way (it was
# not in the state Home Assistant thought), wait a moment and press again.
POWER_CONFIRM_TIMEOUT = 5.0  # seconds
POWER_RETRY_DELAY = 3.0  # seconds

# Some TVs drop off the network for a few seconds now and then while in
# standby, so coming back does not mean the TV was switched on. Only after
# being off the network this long is it treated as a fresh start-up.
LONG_OFFLINE = 600  # seconds

# Pause between repeated key presses so the TV does not drop any (seconds)
KEY_REPEAT_DELAY = 0.3

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

# Inputs the TV really switches to: "TV" closes Netflix/YouTube (back to the
# broadcast), the apps are started via DIAL. Other inputs (HDMI, AV) cannot be
# chosen over the network; the "source" key opens the TV's input menu.
SOURCE_LIST = ["TV", "YouTube", "Netflix"]

# Sources that are started as apps via DIAL: source name -> (DIAL app, Origin)
DIAL_APPS = {
    "Netflix": ("Netflix", None),
    # YouTube only accepts the launch when it comes from YouTube's origin
    "YouTube": ("YouTube", "https://www.youtube.com"),
}

# Apple Home remote (HA HomeKit Bridge fires this event for TV accessories)
HOMEKIT_REMOTE_EVENT = "homekit_tv_remote_key_pressed"

# Apple Home remote key -> TV key name (see KEY_CODES)
HOMEKIT_KEY_MAP = {
    "arrow_up": "up",
    "arrow_down": "down",
    "arrow_left": "left",
    "arrow_right": "right",
    "select": "ok",
    "back": "exit",  # Apple remote back button -> TV Exit key
    "exit": "exit",
    "play_pause": "play",
    "information": "home",
}

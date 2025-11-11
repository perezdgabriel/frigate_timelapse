"""Constants for the Frigate Timelapse integration."""

DOMAIN = "frigate_timelapse"
CONF_FRIGATE_URL = "frigate_url"
CONF_CAMERA = "camera"
CONF_CAPTURE_INTERVAL = "capture_interval"
CONF_OUTPUT_PATH = "output_path"
CONF_FPS = "fps"
CONF_RESOLUTION = "resolution"

DEFAULT_CAPTURE_INTERVAL = 60  # seconds
DEFAULT_FPS = 30
DEFAULT_OUTPUT_PATH = "/media/timelapse"
DEFAULT_RESOLUTION = "1920x1080"

# Services
SERVICE_CAPTURE_IMAGE = "capture_image"
SERVICE_GENERATE_TIMELAPSE = "generate_timelapse"
SERVICE_START_CAPTURE = "start_capture"
SERVICE_STOP_CAPTURE = "stop_capture"

# Attributes
ATTR_CAMERA = "camera"
ATTR_START_TIME = "start_time"
ATTR_END_TIME = "end_time"
ATTR_OUTPUT_FILE = "output_file"
ATTR_IMAGES_COUNT = "images_count"
ATTR_STATUS = "status"
ATTR_LAST_CAPTURE = "last_capture"
ATTR_TIMELAPSE_PATH = "timelapse_path"

# States
STATE_IDLE = "idle"
STATE_CAPTURING = "capturing"
STATE_GENERATING = "generating"
STATE_ERROR = "error"

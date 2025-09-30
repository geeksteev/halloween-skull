"""
Configuration file for the three-eyed skull project
"""

# Display Configuration
DISPLAY_SIZE = 240
DISPLAY_ROTATION = 3  # 90 degrees CCW for column-major rendering

# SPI Configuration
SPI_SPEED_HZ = 50000000  # 50 MHz
SPI_BUS = 0
SPI_DEVICE = 0

# Display Pin Assignments (CS, DC, RST)
DISPLAY_PINS = {
    'left': {'cs': 8, 'dc': 24, 'rst': 25},
    'right': {'cs': 7, 'dc': 23, 'rst': 22},
    'middle': {'cs': 5, 'dc': 6, 'rst': 13}
}

# Camera Configuration
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30
FACE_DETECTION_SCALE = 1.1
FACE_MIN_NEIGHBORS = 5

# Eye Behavior Configuration
EYE_MODES = {
    'TRACKING': 'tracking',
    'WANDERING': 'wandering',
    'REST': 'rest'
}

DEFAULT_MODE = EYE_MODES['TRACKING']

# Eye Movement Parameters
SACCADE_MIN_DURATION = 83000  # microseconds (~1/12 sec)
SACCADE_MAX_DURATION = 166000  # microseconds (~1/6 sec)
MICROSACCADE_MIN_DURATION = 7000  # microseconds
MICROSACCADE_MAX_DURATION = 25000  # microseconds
GAZE_MAX = 3000000  # Max time between major eye movements (3 sec)
FIXATE_CONVERGENCE = 7  # Pixel convergence for eye fixation

# Blink Parameters
BLINK_MIN_DURATION = 36000  # microseconds (~1/28 sec)
BLINK_MAX_DURATION = 72000  # microseconds (~1/14 sec)
BLINK_INTERVAL_MIN = 4000000  # 4 seconds between blinks

# Pupil/Iris Parameters
IRIS_RADIUS = 60  # Approximate size in pixels
IRIS_MIN = 0.45
IRIS_RANGE = 0.35
PUPIL_COLOR = 0x0000  # Black
IRIS_COLOR = 0xFF01  # Default iris color
SCLERA_COLOR = 0xFFFF  # White
BACK_COLOR = 0x0000  # Black
EYELID_COLOR = 0x0000  # Black

# Tracking Parameters
TRACKING_ENABLED = True
TRACK_FACTOR = 0.5

# Inactivity Settings
INACTIVITY_TIMEOUT = 600  # 10 minutes in seconds
LAST_ACTIVITY_CHECK_INTERVAL = 1.0  # Check every second

# DotStar LED Configuration
DOTSTAR_NUM_LEDS = 72  # Adjust to your strip length
DOTSTAR_BRIGHTNESS = 0.5  # 0.0 to 1.0
DOTSTAR_DATA_PIN = 10  # MOSI (shared with SPI)
DOTSTAR_CLOCK_PIN = 11  # SCLK (shared with SPI)

# Default LED Color
DEFAULT_LED_COLOR = (255, 0, 0)  # Red
DEFAULT_LED_PATTERN = 'pulse'

# Audio Configuration
AUDIO_SAMPLE_RATE = 22050
AUDIO_CHANNELS = 1
AUDIO_VOLUME = 0.75

# Audio file paths (relative to sounds/ directory)
SOUND_EFFECTS = {
    'ambient': ['ambient_01.wav', 'ambient_02.wav'],
    'detection': ['whisper_01.wav', 'gasp_01.wav'],
    'scare': ['scream_01.wav', 'laugh_01.wav']
}

# SD Card Configuration for Audio
SD_CARD_CS_PIN = 16
AUDIO_BASE_PATH = '/home/pi/skull_project/sounds/'

# IR LED Configuration
IR_LED_PIN = 17
IR_LED_ENABLED = True

# Debug Settings
DEBUG_MODE = True
SHOW_FPS = True
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
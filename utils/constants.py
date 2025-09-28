"""Application constants and configuration."""

# Supported image file extensions
SUPPORTED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

# Default directories
DEFAULT_IMAGES_DIR = "data/images"
DEFAULT_LABELS_DIR = "data/labels"

# UI Configuration
DEFAULT_WINDOW_SIZE = "1200x800"
MIN_WINDOW_SIZE = (800, 600)
GRID_COLUMNS = 4
THUMBNAIL_SIZE = (150, 150)

# Zoom Configuration
MIN_ZOOM = 0.1  # Minimum zoom (10% of original size)
MAX_ZOOM_MOUSE = 2.0  # Maximum zoom for mouse wheel (200%)
MAX_ZOOM_KEYBOARD = 2.0  # Maximum zoom for keyboard shortcuts (200%)
ZOOM_COOLDOWN = 50  # milliseconds between zoom operations
ZOOM_INCREMENT_KEYBOARD = 1.1  # Zoom increment for keyboard
ZOOM_INCREMENT_MOUSE = 1.05  # Zoom increment for mouse wheel (smoother)

# Drawing Configuration
MIN_BOX_SIZE = 5  # Minimum bounding box size in pixels
BOX_OUTLINE_COLOR = "red"
BOX_OUTLINE_WIDTH = 2
DEFAULT_CLASS_ID = 0

# Canvas Configuration
CANVAS_MARGIN = 0.9  # 90% to leave some margin when fitting image
SCROLLBAR_WIDTH = 15

# File I/O Configuration
LABEL_FILE_EXTENSION = ".txt"
COORDINATE_PRECISION = 6  # Decimal places for normalized coordinates

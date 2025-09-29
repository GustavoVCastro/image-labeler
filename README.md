# Image Labeler

A GUI application for labeling images with bounding boxes in YOLO format.

## Project Structure

The application has been modularized into the following components:

### Core Modules (`core/`)
- **`image_manager.py`** - Handles image loading, scaling, and coordinate transformations
- **`label_manager.py`** - Manages bounding box labels and file I/O operations
- **`zoom_manager.py`** - Handles cursor-centered zoom and pan functionality with smooth animations

### UI Modules (`ui/`)
- **`main_window.py`** - Main application window and menu setup
- **`grid_view.py`** - Thumbnail grid view for browsing images
- **`labeling_view.py`** - Canvas-based labeling interface for drawing bounding boxes
- **`controls.py`** - Navigation, zoom, and information display widgets

### Utilities (`utils/`)
- **`constants.py`** - Application constants and configuration
- **`file_utils.py`** - File and directory utility functions

### Main Application
- **`main.py`** - Entry point and application orchestration
- **`main_original.py`** - Original monolithic version (backup)

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

The application will automatically load images from the `images/` directory if it exists, or you can use File > Open Image Directory to select a different folder.

## Features

- **Grid View**: Browse images as thumbnails in a scrollable grid
- **Labeling Interface**: Draw bounding boxes by holding Ctrl and dragging
- **Zoom & Pan**: Smooth scaling and pan support
- **Image Information**: Current filename and image counter displayed in labeling view
- **Keyboard Shortcuts**:
  - **Navigation**: `←`/`→` (Previous/Next image), `↑`/`↓` (Scroll grid), `q` (Back to grid view)
  - **Zoom**: `f` (Fit to canvas), `1` (100% zoom), `2` (200% zoom), `Ctrl++`/`Ctrl+-` (Zoom in/out)
  - **Labeling**: `Ctrl+z` (Undo bounding box), `Ctrl+Backspace` (Clear all labels)
  - **Alternative Zoom**: `Ctrl+0` (Fit), `Ctrl+1` (100%), `Ctrl+2` (200%)
- **Auto-save**: Labels are automatically saved in YOLO format

## Directory Structure

```
image-labeler/
├── images/          # Input images (auto-loaded)
├── labels/          # Output YOLO format labels
├── input/           # Alternative input directory
├── core/            # Core functionality modules
├── ui/              # User interface modules
├── utils/           # Utility functions and constants
├── scripts/         # Additional utility scripts
└── main.py          # Application entry point
```

## Label Format

Labels are saved in YOLO format with normalized coordinates:
```
class_id x_center y_center width height
```

Where all coordinates are normalized to [0,1] relative to image dimensions.

## Modular Architecture Benefits

The refactored codebase provides:
- **Separation of Concerns**: Each module has a specific responsibility
- **Maintainability**: Easier to modify and extend individual components
- **Testability**: Components can be tested in isolation
- **Reusability**: Modules can be reused in other projects
- **Readability**: Smaller, focused files are easier to understand
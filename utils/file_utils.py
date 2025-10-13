"""File and directory utility functions."""

import os
from typing import List
from .constants import SUPPORTED_EXTENSIONS


def create_directories(*dirs: str) -> None:
    """Create directories if they don't exist."""
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)


def get_image_files(directory: str) -> List[str]:
    """Get list of image files from a directory."""
    if not os.path.exists(directory):
        return []

    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith(SUPPORTED_EXTENSIONS)
    ]


def get_label_file_path(image_path: str, labels_dir: str) -> str:
    """Get the corresponding label file path for an image."""
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    return os.path.join(labels_dir, f"{image_name}.txt")


def delete_file_if_exists(file_path: str) -> bool:
    """Delete a file if it exists. Returns True if deleted, False otherwise."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
        return False

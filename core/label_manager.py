"""Label management for bounding boxes."""

import os
from typing import List, Tuple
from utils.constants import DEFAULT_CLASS_ID, COORDINATE_PRECISION
from utils.file_utils import get_label_file_path, delete_file_if_exists


class LabelManager:
    """Manages bounding box labels for images."""

    def __init__(self, labels_dir: str):
        self.labels_dir = labels_dir
        self.boxes: List[Tuple[float, float, float, float, float]] = (
            []
        )  # class_id, x_center, y_center, width, height

    def clear_boxes(self) -> None:
        """Clear all bounding boxes."""
        self.boxes.clear()

    def add_box(
        self,
        x_center: float,
        y_center: float,
        width: float,
        height: float,
        class_id: float = DEFAULT_CLASS_ID,
    ) -> None:
        """Add a bounding box with normalized coordinates."""
        self.boxes.append((class_id, x_center, y_center, width, height))

    def remove_last_box(self) -> bool:
        """Remove the last bounding box. Returns True if a box was removed."""
        if self.boxes:
            self.boxes.pop()
            return True
        return False

    def get_boxes(self) -> List[Tuple[float, float, float, float, float]]:
        """Get all bounding boxes."""
        return self.boxes.copy()

    def load_labels(self, image_path: str) -> bool:
        """Load labels from file for the given image. Returns True if labels were loaded."""
        self.clear_boxes()

        if not image_path:
            return False

        label_path = get_label_file_path(image_path, self.labels_dir)

        if not os.path.exists(label_path):
            return False

        try:
            with open(label_path, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_id, x_center, y_center, width, height = map(float, parts)
                        self.boxes.append((class_id, x_center, y_center, width, height))
            return True
        except Exception as e:
            print(f"Error loading labels from {label_path}: {e}")
            return False

    def save_labels(self, image_path: str) -> bool:
        """Save labels to file for the given image. Returns True if successful."""
        if not image_path:
            return False

        label_path = get_label_file_path(image_path, self.labels_dir)

        try:
            with open(label_path, "w") as f:
                for class_id, x_center, y_center, width, height in self.boxes:
                    f.write(
                        f"{class_id} {x_center:.{COORDINATE_PRECISION}f} {y_center:.{COORDINATE_PRECISION}f} "
                        f"{width:.{COORDINATE_PRECISION}f} {height:.{COORDINATE_PRECISION}f}\n"
                    )
            return True
        except Exception as e:
            print(f"Error saving labels to {label_path}: {e}")
            return False

    def delete_labels(self, image_path: str) -> bool:
        """Delete the label file for the given image. Returns True if deleted."""
        if not image_path:
            return False

        label_path = get_label_file_path(image_path, self.labels_dir)
        return delete_file_if_exists(label_path)

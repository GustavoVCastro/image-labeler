import os
from pathlib import Path

# Define paths
images_folder = Path("images")
labels_folder = Path("labels")

# Create labels folder if it doesn't exist
labels_folder.mkdir(exist_ok=True)

# Image extensions to check
image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}

# Get all image files
image_files = [f for f in images_folder.iterdir() 
               if f.is_file() and f.suffix.lower() in image_extensions]

print(f"Found {len(image_files)} images")

# Check each image for corresponding label
created_count = 0
for img_file in image_files:
    # Get the label file path (same name, .txt extension)
    label_file = labels_folder / f"{img_file.stem}.txt"
    
    # Create empty label file if it doesn't exist
    if not label_file.exists():
        label_file.touch()
        created_count += 1
        print(f"Created: {label_file.name}")

print(f"\nDone! Created {created_count} empty label files.")

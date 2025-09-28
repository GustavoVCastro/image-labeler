#!/usr/bin/env python3
"""
Image Resizer Utility

This script resizes images so that their smallest side becomes 640px while preserving aspect ratio.
All images are converted to JPEG format and saved to the output directory.

Usage:
    python image_resizer.py <input_directory> <output_directory>
"""

import os
import sys
import argparse
from PIL import Image
from pathlib import Path


def resize_image(input_path, output_path, target_size=640):
    """
    Resize an image so that its smallest side becomes target_size pixels.
    Preserves aspect ratio and converts to JPEG format.
    Handles EXIF orientation data to prevent rotation issues (especially with HEIC).
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save resized image
        target_size (int): Target size for smallest side (default: 640)
    """
    try:
        # Open the image
        with Image.open(input_path) as img:
            # Handle EXIF orientation data to prevent rotation issues
            img = fix_image_orientation(img)
            
            # Convert to RGB if necessary (for JPEG compatibility)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Get original dimensions
            width, height = img.size
            
            # Calculate new dimensions
            if width < height:
                # Width is smaller, scale based on width
                new_width = target_size
                new_height = int((height * target_size) / width)
            else:
                # Height is smaller, scale based on height
                new_height = target_size
                new_width = int((width * target_size) / height)
            
            # Resize the image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save as JPEG (remove EXIF data to prevent orientation issues)
            resized_img.save(output_path, 'JPEG', quality=95, optimize=True)
            
            print(f"Resized: {input_path} -> {output_path} ({width}x{height} -> {new_width}x{new_height})")
            
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")


def fix_image_orientation(img):
    """
    Fix image orientation based on EXIF data.
    This prevents HEIC and other images from being rotated incorrectly.
    
    Args:
        img (PIL.Image): PIL Image object
        
    Returns:
        PIL.Image: Corrected image
    """
    try:
        # Check if image has EXIF data
        if hasattr(img, '_getexif'):
            exif = img._getexif()
            if exif is not None:
                # Get orientation tag (274)
                orientation = exif.get(274, 1)
                
                # Apply rotation based on orientation value
                if orientation == 2:
                    # Mirror horizontally
                    img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                elif orientation == 3:
                    # Rotate 180 degrees
                    img = img.transpose(Image.Transpose.ROTATE_180)
                elif orientation == 4:
                    # Mirror vertically
                    img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                elif orientation == 5:
                    # Mirror horizontally then rotate 90 degrees counter-clockwise
                    img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                    img = img.transpose(Image.Transpose.ROTATE_90)
                elif orientation == 6:
                    # Rotate 90 degrees clockwise
                    img = img.transpose(Image.Transpose.ROTATE_270)
                elif orientation == 7:
                    # Mirror horizontally then rotate 90 degrees clockwise
                    img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                    img = img.transpose(Image.Transpose.ROTATE_270)
                elif orientation == 8:
                    # Rotate 90 degrees counter-clockwise
                    img = img.transpose(Image.Transpose.ROTATE_90)
    except Exception as e:
        # If EXIF processing fails, continue with original image
        print(f"Warning: Could not process EXIF data: {str(e)}")
    
    return img


def get_image_files(directory):
    """
    Get all image files from a directory.
    
    Args:
        directory (str): Directory path
        
    Returns:
        list: List of image file paths
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp', '.gif', '.heic', '.heif'}
    image_files = []
    
    for file_path in Path(directory).rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(file_path)
    
    return image_files


def main():
    parser = argparse.ArgumentParser(
        description='Resize images so smallest side becomes 640px while preserving aspect ratio'
    )
    parser.add_argument('input_dir', help='Input directory containing images')
    parser.add_argument('output_dir', help='Output directory for resized images')
    parser.add_argument('--size', type=int, default=640, 
                       help='Target size for smallest side (default: 640)')
    
    args = parser.parse_args()
    
    # Validate input directory
    if not os.path.isdir(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' does not exist.")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Get all image files
    image_files = get_image_files(args.input_dir)
    
    if not image_files:
        print(f"No image files found in '{args.input_dir}'")
        sys.exit(1)
    
    print(f"Found {len(image_files)} image(s) to process...")
    
    # Process each image
    processed_count = 0
    for image_path in image_files:
        # Create output filename (change extension to .jpg)
        relative_path = image_path.relative_to(Path(args.input_dir))
        output_filename = relative_path.with_suffix('.jpg')
        output_path = Path(args.output_dir) / output_filename
        
        # Create subdirectories if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Resize the image
        resize_image(str(image_path), str(output_path), args.size)
        processed_count += 1
    
    print(f"\nProcessing complete! {processed_count} images processed.")


if __name__ == '__main__':
    main()
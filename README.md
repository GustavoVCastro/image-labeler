# Image Resizer Utility

A Python utility script that resizes images so that their smallest side becomes 640px while preserving aspect ratio. All images are converted to JPEG format.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python image_resizer.py <input_directory> <output_directory>
```

### Options

- `--size SIZE`: Target size for smallest side (default: 640)

### Examples

```bash
# Resize images with default 640px smallest side
python image_resizer.py ./images ./resized_images

# Resize images with 512px smallest side
python image_resizer.py ./images ./resized_images --size 512
```

## Features

- Preserves aspect ratio
- Converts all images to JPEG format
- Supports multiple image formats (JPG, PNG, BMP, TIFF, WebP, GIF, HEIC)
- **Automatic orientation correction** for HEIC and other images with EXIF data
- Recursively processes subdirectories
- High-quality resizing using Lanczos resampling
- Creates output directory structure matching input structure
- Comprehensive error handling

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff, .tif)
- WebP (.webp)
- GIF (.gif)
- HEIC (.heic, .heif) - with automatic orientation correction
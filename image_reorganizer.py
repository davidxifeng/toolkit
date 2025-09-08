#!/usr/bin/env python3
"""
Image Reorganizer - Convert horizontally concatenated images to 2D grid layout
"""

import argparse
import math
import sys
from pathlib import Path
from PIL import Image


def analyze_image(image_path, sub_width=None):
    """
    Analyze the composite image and determine sub-image count and dimensions.
    
    Args:
        image_path: Path to the composite image
        sub_width: Width of each sub-image (defaults to image height)
    
    Returns:
        tuple: (PIL.Image object, num_images, sub_width, sub_height)
    """
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        # Default sub_width to height (assuming square images)
        if sub_width is None:
            sub_width = height
            
        # Calculate number of sub-images
        if width % sub_width != 0:
            print(f"Warning: Image width {width} is not divisible by sub-width {sub_width}")
            print(f"This may result in incomplete sub-images")
        
        num_images = width // sub_width
        sub_height = height
        
        print(f"Image dimensions: {width} x {height}")
        print(f"Sub-image dimensions: {sub_width} x {sub_height}")
        print(f"Number of sub-images: {num_images}")
        
        return img, num_images, sub_width, sub_height
        
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        sys.exit(1)


def find_best_layout(num_images, show_options=False):
    """
    Find the most square-like layout for the given number of images.
    
    Args:
        num_images: Number of images to arrange
        show_options: Whether to display all layout options
        
    Returns:
        tuple: (rows, cols) representing the grid layout
    """
    if num_images <= 0:
        return (0, 0)
        
    best_ratio = float('inf')
    best_layout = (num_images, 1)
    layout_options = []
    
    # Try all possible row counts up to sqrt(num_images) + 1
    max_rows = int(math.sqrt(num_images)) + 2
    
    for rows in range(1, max_rows):
        cols = math.ceil(num_images / rows)  # Round up to fit all images
        
        # Calculate aspect ratio (larger dimension / smaller dimension)
        ratio = max(rows, cols) / min(rows, cols)
        
        # Prefer layouts that waste less space and have better aspect ratio
        total_cells = rows * cols
        wasted_space = total_cells - num_images
        
        # Combined score: aspect ratio + penalty for wasted space
        score = ratio + (wasted_space * 0.1)
        
        layout_options.append((rows, cols, ratio, wasted_space, score))
        
        if score < best_ratio:
            best_ratio = score
            best_layout = (rows, cols)
    
    if show_options:
        print("\nLayout options (rows x cols, aspect ratio, empty cells, score):")
        for rows, cols, ratio, wasted, score in sorted(layout_options, key=lambda x: x[4]):
            marker = "* " if (rows, cols) == best_layout else "  "
            print(f"{marker}{rows}x{cols} - ratio: {ratio:.2f}, empty: {wasted}, score: {score:.2f}")
    
    return best_layout


def create_grid_image(img, num_images, sub_width, sub_height, rows, cols, scale_factor=1.0):
    """
    Create a 2D grid layout from the horizontally concatenated image.
    
    Args:
        img: PIL Image object of the composite image
        num_images: Number of sub-images
        sub_width: Width of each sub-image
        sub_height: Height of each sub-image
        rows: Number of rows in the grid
        cols: Number of columns in the grid
        scale_factor: Scale factor for the output image
        
    Returns:
        PIL Image object of the grid layout
    """
    # Calculate output dimensions
    output_sub_width = int(sub_width * scale_factor)
    output_sub_height = int(sub_height * scale_factor)
    output_width = output_sub_width * cols
    output_height = output_sub_height * rows
    
    # Create new blank image
    grid_img = Image.new('RGB', (output_width, output_height), color='white')
    
    print(f"Creating {rows}x{cols} grid with {output_width}x{output_height} output dimensions")
    
    # Extract and place each sub-image
    for i in range(num_images):
        # Calculate source position (horizontal strip)
        src_x = i * sub_width
        src_y = 0
        
        # Extract sub-image
        sub_img = img.crop((src_x, src_y, src_x + sub_width, src_y + sub_height))
        
        # Scale if needed
        if scale_factor != 1.0:
            sub_img = sub_img.resize((output_sub_width, output_sub_height), Image.Resampling.LANCZOS)
        
        # Calculate destination position in grid
        row = i // cols
        col = i % cols
        dst_x = col * output_sub_width
        dst_y = row * output_sub_height
        
        # Paste sub-image into grid
        grid_img.paste(sub_img, (dst_x, dst_y))
        
        if (i + 1) % 5 == 0 or i == num_images - 1:
            print(f"Processed {i + 1}/{num_images} images")
    
    return grid_img


def main():
    parser = argparse.ArgumentParser(
        description="Convert horizontally concatenated images to 2D grid layout"
    )
    parser.add_argument("input", help="Input image file path")
    parser.add_argument("--sub-width", type=int, 
                       help="Width of each sub-image (default: image height)")
    parser.add_argument("--scale", type=float, default=1.0,
                       help="Scale factor for output image (default: 1.0)")
    parser.add_argument("--output", 
                       help="Output file path (default: input_grid.png)")
    parser.add_argument("--show-layouts", action="store_true",
                       help="Show all possible layout options")
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    
    # Set default output path
    if args.output is None:
        args.output = input_path.stem + "_grid" + input_path.suffix
    
    # Analyze the input image
    print(f"Analyzing image: {args.input}")
    img, num_images, sub_width, sub_height = analyze_image(args.input, args.sub_width)
    
    # Calculate optimal layout
    rows, cols = find_best_layout(num_images, args.show_layouts)
    print(f"Optimal layout: {rows} rows x {cols} columns")
    print(f"Grid will have {rows * cols - num_images} empty cells")
    
    print(f"Scale factor: {args.scale}")
    print(f"Output file: {args.output}")
    
    # Create the grid layout
    print("\nCreating grid layout...")
    grid_img = create_grid_image(img, num_images, sub_width, sub_height, rows, cols, args.scale)
    
    # Save the result
    print(f"\nSaving result to: {args.output}")
    try:
        grid_img.save(args.output)
        print(f"Success! Grid image saved with dimensions: {grid_img.size}")
    except Exception as e:
        print(f"Error saving image: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
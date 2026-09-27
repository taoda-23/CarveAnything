#!/usr/bin/env python3
"""
TAP Test Suite for Image Pipeline Verification.
Tests custom photos or generates synthetic heightmaps for CNC carving verification.
"""

import sys
import os
import math
from PIL import Image, ImageOps

print("1..4")

# Determine if a custom input image was supplied as an argument
USING_CUSTOM_IMAGE = len(sys.argv) > 1
if USING_CUSTOM_IMAGE:
    SAMPLE_IMAGE_PATH = sys.argv[1]
else:
    SAMPLE_IMAGE_PATH = "/app/pics/bas_relief_sample.png"

def run_test(test_id, description, test_func):
    try:
        success, message = test_func()
        if success:
            msg_str = f" # {message}" if message else ""
            print(f"ok {test_id} - {description}{msg_str}")
        else:
            print(f"not ok {test_id} - {description} # {message}")
    except Exception as e:
        print(f"not ok {test_id} - {description} # Exception: {e}")

# Test 1: Verify volume directory accessibility
def test_dir_writable():
    target_dir = "/app/pics"
    os.makedirs(target_dir, exist_ok=True)
    test_file = os.path.join(target_dir, ".tap_write_test")
    with open(test_file, "w") as f:
        f.write("tap_ok")
    if os.path.exists(test_file):
        os.remove(test_file)
        return True, ""
    return False, "Directory not writable"

# Test 2: Generate synthetic heightmap OR validate custom user image path
def test_prepare_image():
    if USING_CUSTOM_IMAGE:
        if os.path.exists(SAMPLE_IMAGE_PATH):
            return True, f"Custom image loaded: {os.path.basename(SAMPLE_IMAGE_PATH)}"
        return False, f"Custom image file not found: {SAMPLE_IMAGE_PATH}"
    
    # Generate synthetic image only when NO custom image argument was passed
    width, height = 512, 512
    center_x, center_y = width // 2, height // 2
    max_radius = width // 2 - 20
    
    img = Image.new("L", (width, height), color=0)
    pixels = img.load()
    
    for x in range(width):
        for y in range(height):
            dx = x - center_x
            dy = y - center_y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < max_radius:
                normalized_dist = dist / max_radius
                dome_height = math.cos(normalized_dist * (math.pi / 2))
                ring_pattern = (math.sin(normalized_dist * math.pi * 8) + 1.0) / 2.0 * 0.15
                pixel_val = int(255 * (dome_height * 0.85 + ring_pattern))
                pixels[x, y] = min(255, max(0, pixel_val))
                
    img.save(SAMPLE_IMAGE_PATH)
    
    if os.path.exists(SAMPLE_IMAGE_PATH) and os.path.getsize(SAMPLE_IMAGE_PATH) > 0:
        return True, "Generated synthetic test dome"
    return False, "Failed to generate synthetic heightmap image"

# Test 3: Validate depth map resolution and integrity
def test_open_image():
    if not os.path.exists(SAMPLE_IMAGE_PATH):
        return False, f"File missing: {SAMPLE_IMAGE_PATH}"
    with Image.open(SAMPLE_IMAGE_PATH) as img:
        img.verify()
    return True, ""

# Test 4: Simulate CNC Pre-processing (Autocontrast & Depth Map Export)
def test_process_heightmap():
    if not os.path.exists(SAMPLE_IMAGE_PATH):
        return False, f"File missing: {SAMPLE_IMAGE_PATH}"
    
    # Save output with a distinct name so original input is untouched
    file_stem = os.path.splitext(os.path.basename(SAMPLE_IMAGE_PATH))[0]
    out_path = f"/app/pics/{file_stem}_cnc_heightmap.png"
    
    with Image.open(SAMPLE_IMAGE_PATH) as img:
        grayscale = img.convert("L")
        depth_map = ImageOps.autocontrast(grayscale)
        depth_map.save(out_path)
        
        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            return True, f"Output written to {os.path.basename(out_path)}"
    return False, "Failed to generate heightmap output"

if __name__ == "__main__":
    run_test(1, "Check /app/pics volume writability", test_dir_writable)
    run_test(2, "Prepare input image", test_prepare_image)
    run_test(3, "Validate depth map image integrity", test_open_image)
    run_test(4, "Process image to CNC heightmap output", test_process_heightmap)
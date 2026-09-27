#!/usr/bin/env python3
"""
TAP Test Suite for Image Pipeline Verification.
Outputs standard Test Anything Protocol (TAP) format.
"""

import sys
import os
import urllib.request
from PIL import Image

# TAP Plan: We intend to run 4 tests
print("1..4")

def run_test(test_id, description, test_func):
    """Executes a test function and prints TAP-compliant status."""
    try:
        success, message = test_func()
        if success:
            print(f"ok {test_id} - {description}")
        else:
            print(f"not ok {test_id} - {description} # {message}")
    except Exception as e:
        print(f"not ok {test_id} - {description} # Exception: {e}")

# Test 1: Verify output/shared volume directory exists and is writable
def test_dir_writable():
    target_dir = "/app/pics"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
    
    test_file = os.path.join(target_dir, ".tap_write_test")
    with open(test_file, "w") as f:
        f.write("tap_ok")
    
    is_writable = os.path.exists(test_file)
    if is_writable:
        os.remove(test_file)
        return True, ""
    return False, "Directory not writable"

# Test 2: Fetch a small open-source CC0 test image (1x1 PNG or small test icon)
SAMPLE_IMAGE_PATH = "/app/pics/sample_test_image.png"
SAMPLE_URL = "https://raw.githubusercontent.com/mathiasbynens/small/master/png-transparent.png"

def test_download_image():
    urllib.request.urlretrieve(SAMPLE_URL, SAMPLE_IMAGE_PATH)
    if os.path.exists(SAMPLE_IMAGE_PATH) and os.path.getsize(SAMPLE_IMAGE_PATH) > 0:
        return True, ""
    return False, f"Failed to download image from {SAMPLE_URL}"

# Test 3: Verify the image can be loaded and parsed by Pillow/PIL
def test_open_image():
    with Image.open(SAMPLE_IMAGE_PATH) as img:
        img.verify()
    return True, ""

# Test 4: Verify image conversion/processing capability (e.g., Grayscale for CNC carving)
def test_process_image():
    with Image.open(SAMPLE_IMAGE_PATH) as img:
        gray_img = img.convert("L")
        out_path = "/app/pics/sample_test_grayscale.png"
        gray_img.save(out_path)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            return True, ""
    return False, "Failed to convert and save processed image"

# Execute Test Plan
if __name__ == "__main__":
    run_test(1, "Check /app/pics volume writability", test_dir_writable)
    run_test(2, "Fetch open-source CC0 sample image", test_download_image)
    run_test(3, "Validate sample image integrity with PIL", test_open_image)
    run_test(4, "Process image to grayscale output", test_process_image)
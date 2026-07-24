"""
Test the attendance system components
Run this to see exactly what's failing
"""

import os
import sys

print("=" * 60)
print("ATTENDANCE SYSTEM TEST")
print("=" * 60)

# Test 1: Check if faces folder has images
print("\n[1] Checking faces directory...")
if os.path.isdir('faces'):
    images = [f for f in os.listdir('faces') if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if images:
        print(f"  ✓ Found {len(images)} face image(s)")
        for img in images:
            print(f"    - {img}")
    else:
        print("  ✗ NO FACE IMAGES FOUND!")
        print("    -> Add .jpg files to faces/ folder to use the system")
        sys.exit(1)
else:
    print("  ✗ faces/ folder not found")
    sys.exit(1)

# Test 2: Try loading face_recognition
print("\n[2] Loading face_recognition library...")
try:
    import face_recognition
    print("  ✓ face_recognition imported")
except Exception as e:
    print(f"  ✗ Failed to import: {e}")
    sys.exit(1)

# Test 3: Try loading a face image
print("\n[3] Testing face detection on first image...")
try:
    import cv2
    import numpy as np
    
    face_file = images[0]
    image_path = os.path.join('faces', face_file)
    
    print(f"  Loading: {image_path}")
    img = cv2.imread(image_path)
    if img is None:
        print(f"  ✗ Could not read image")
        sys.exit(1)
    
    print(f"  Image size: {img.shape}")
    
    # Convert to RGB
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    print("  ✓ Converted to RGB")
    
    # Find faces
    face_locations = face_recognition.face_locations(rgb_img)
    print(f"  ✓ Faces found: {len(face_locations)}")
    
    if len(face_locations) == 0:
        print("  ✗ NO FACES DETECTED IN IMAGE!")
        print("    -> Image must have a clear face")
        print("    -> Try using a different image")
        sys.exit(1)
    
    # Get encodings
    face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
    print(f"  ✓ Face encodings created: {len(face_encodings)}")
    
    if len(face_encodings) == 0:
        print("  ✗ COULD NOT ENCODE FACE!")
        sys.exit(1)
    
    encoding = face_encodings[0]
    print(f"  ✓ Encoding size: {encoding.shape}")
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Try camera
print("\n[4] Testing camera...")
try:
    import cv2
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("  ✗ Could not open camera")
        print("    -> Check camera is connected")
        sys.exit(1)
    
    ret, frame = cap.read()
    if not ret:
        print("  ✗ Could not read frame from camera")
        sys.exit(1)
    
    print(f"  ✓ Camera working, resolution: {frame.shape[1]}x{frame.shape[0]}")
    cap.release()
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    sys.exit(1)

# Test 5: Try importing attendence module
print("\n[5] Testing attendence module...")
try:
    import attendence
    print("  ✓ attendence module imported")
    print(f"  - Loaded {len(attendence.encodeListKnown)} known faces")
    print(f"  - Known names: {attendence.classNames}")
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED ✓")
print("=" * 60)
print("\nYou can now run: python main.py")

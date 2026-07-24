"""
Minimal test to check if attendance works
This simulates clicking "Start Attendance" without the GUI
"""

import os
import sys

print("=" * 60)
print("ATTENDANCE SYSTEM - MINIMAL TEST")
print("=" * 60)

# Step 1: Check faces
print("\n[Step 1] Checking faces directory...")
if not os.path.isdir('faces'):
    print("  ✗ faces/ folder not found!")
    sys.exit(1)

images = [f for f in os.listdir('faces') if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
if not images:
    print("  ✗ No face images in faces/ folder!")
    print("  -> Add .jpg files to faces/ folder first")
    sys.exit(1)

print(f"  ✓ Found {len(images)} face image(s): {images}")

# Step 2: Import modules
print("\n[Step 2] Importing modules...")
try:
    import numpy as np
    import cv2
    import face_recognition
    print("  ✓ Core libraries loaded")
except ImportError as e:
    print(f"  ✗ Missing library: {e}")
    sys.exit(1)

# Step 3: Load attendence module
print("\n[Step 3] Loading attendence module...")
try:
    import attendence
    print("  ✓ Attendence module imported")
except Exception as e:
    print(f"  ✗ Error importing attendence: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Load known faces
print("\n[Step 4] Loading known faces...")
try:
    attendence.load_known_faces()
    num_faces = len(attendence.encodeListKnown)
    if num_faces == 0:
        print("  ✗ No faces were loaded!")
        print("  -> Images must contain clear, frontal faces")
        sys.exit(1)
    print(f"  ✓ Loaded {num_faces} face(s)")
    print(f"  - Known names: {attendence.classNames}")
except Exception as e:
    print(f"  ✗ Error loading faces: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Test camera
print("\n[Step 5] Testing camera...")
try:
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("  ✗ Camera not accessible")
        print("  -> Check camera is connected and not in use")
        sys.exit(1)
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("  ✗ Camera returned empty frame")
        sys.exit(1)
        
    print(f"  ✓ Camera working: {frame.shape[1]}x{frame.shape[0]}")
except Exception as e:
    print(f"  ✗ Camera error: {e}")
    sys.exit(1)

# Step 6: Test face detection on camera frame
print("\n[Step 6] Testing face detection on camera...")
try:
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    print("  Opening camera for 3 seconds...")
    
    frame_count = 0
    faces_found = False
    
    for i in range(30):  # Try for ~1 second (assuming 30 fps)
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Scale down for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame)
        frame_count += 1
        
        if face_locations:
            faces_found = True
            print(f"  ✓ Detected {len(face_locations)} face(s) in frame {frame_count}")
            break
    
    cap.release()
    
    if not faces_found:
        print(f"  ✗ No faces detected in {frame_count} frames")
        print("  -> Try moving closer to camera or improving lighting")
    else:
        print("  ✓ Face detection working!")
        
except Exception as e:
    print(f"  ✗ Error testing face detection: {e}")
    cap.release()

print("\n" + "=" * 60)
print("TEST COMPLETE ✓")
print("=" * 60)
print("\nYou can now run: python main.py")
print("Click 'Start Attendance' and look at the camera")

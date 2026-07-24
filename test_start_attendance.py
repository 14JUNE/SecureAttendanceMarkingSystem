#!/usr/bin/env python3
"""Test if start_attendance can initialize"""
import os
import sys

print("=" * 60)
print("START ATTENDANCE INITIALIZATION TEST")
print("=" * 60)

# Import the module
print("\n[1] Importing attendence module...")
try:
    from SmartAttendence import attendence
    print("✓ Imported successfully")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# Load faces
print("\n[2] Loading faces...")
try:
    attendence.load_known_faces()
    num_faces = len(attendence.encodeListKnown)
    print(f"✓ Loaded {num_faces} faces")
    print(f"  Names: {attendence.classNames}")
    
    if num_faces == 0:
        print("⚠️  WARNING: No faces loaded - attendance won't work!")
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check if camera can be initialized
print("\n[3] Checking camera...")
try:
    import cv2
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    is_open = cap.isOpened()
    
    if is_open:
        print("✓ Camera found and accessible")
        # Try to read one frame
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"✓ Can read frames ({frame.shape[0]}x{frame.shape[1]})")
        else:
            print("⚠️  Camera present but cannot read frames")
        cap.release()
    else:
        print("❌ Camera not accessible")
        print("   Possible solutions:")
        print("   - Check if camera is connected")
        print("   - Check if another app is using the camera")
        print("   - Check camera permissions")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Check if all required directories exist
print("\n[4] Checking directories...")
required_dirs = ['faces', 'attendance', 'logs', 'screenshots']
all_exist = True
for d in required_dirs:
    exists = os.path.isdir(d)
    status = "✓" if exists else "❌"
    print(f"  {status} {d}/")
    if not exists:
        all_exist = False
        os.makedirs(d, exist_ok=True)
        print(f"    → Created {d}/")

# Summary
print("\n" + "=" * 60)
if num_faces > 0:
    print("✓ READY: System is ready to start attendance!")
    print("  Run: python main.py")
else:
    print("❌ NOT READY: No faces loaded")
    print("  Add face images to the 'faces' folder first")
print("=" * 60)

"""
Smart Attendance System - Diagnostic Test
Run this script to check if everything is set up correctly
"""

import os
import sys

print("=" * 60)
print("SMART ATTENDANCE SYSTEM - DIAGNOSTIC TEST")
print("=" * 60)

# Test 1: Check directories
print("\n[1] Checking directories...")
directories = ['faces', 'attendance', 'logs', 'screenshots', 'unknown']
for dir_name in directories:
    exists = os.path.isdir(dir_name)
    print(f"  {'✓' if exists else '✗'} {dir_name}/ exists")
    if not exists:
        os.makedirs(dir_name, exist_ok=True)
        print(f"    -> Created {dir_name}/")

# Test 2: Check Python packages
print("\n[2] Checking Python packages...")
packages = ['cv2', 'face_recognition', 'numpy', 'pandas', 'tkinter']
missing = []
for pkg in packages:
    try:
        __import__(pkg)
        print(f"  ✓ {pkg}")
    except ImportError:
        print(f"  ✗ {pkg} - NOT INSTALLED")
        missing.append(pkg)

if missing:
    print(f"\n  Missing packages: {', '.join(missing)}")
    print("  Run: pip install " + " ".join(missing))

# Test 3: Check face images
print("\n[3] Checking registered faces...")
if os.path.isdir('faces'):
    faces = [f for f in os.listdir('faces') if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if faces:
        print(f"  ✓ Found {len(faces)} face image(s):")
        for face in faces:
            print(f"    - {face}")
    else:
        print("  ✗ No face images found")
        print("    -> Add images to faces/ folder (format: firstname_lastname.jpg)")
else:
    print("  ✗ faces/ folder not found")

# Test 4: Check camera
print("\n[4] Checking camera...")
try:
    import cv2
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if cap.isOpened():
        print("  ✓ Camera detected and working")
        ret, frame = cap.read()
        if ret:
            print(f"    Resolution: {frame.shape[1]}x{frame.shape[0]}")
        cap.release()
    else:
        print("  ✗ Camera not accessible")
        print("    -> Check if camera is connected")
        print("    -> Check if another app is using the camera")
except Exception as e:
    print(f"  ✗ Error accessing camera: {e}")

# Test 5: Check file permissions
print("\n[5] Checking file permissions...")
test_file = 'logs/test.txt'
try:
    with open(test_file, 'w') as f:
        f.write('test')
    with open(test_file, 'r') as f:
        content = f.read()
    os.remove(test_file)
    print("  ✓ Can read/write files")
except Exception as e:
    print(f"  ✗ File permission error: {e}")

# Test 6: Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if not missing:
    print("✓ All packages installed")
else:
    print(f"✗ Missing {len(missing)} package(s)")

print(f"✓ Directories ready")

if os.path.isdir('faces'):
    faces = [f for f in os.listdir('faces') if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if faces:
        print(f"✓ {len(faces)} face(s) registered")
    else:
        print("✗ No faces registered (attendance won't work)")
else:
    print("✗ faces/ folder missing")

print("\n" + "=" * 60)
print("READY TO START: python main.py")
print("=" * 60)

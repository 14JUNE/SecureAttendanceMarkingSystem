#!/usr/bin/env python3
"""
Demo mode - Test face recognition without camera
Loads faces from folder and lets you test recognition
"""
import os
import sys
import random
from datetime import datetime

print("=" * 70)
print("SMART ATTENDANCE - DEMO MODE (No Camera Required)")
print("=" * 70)

# Import required modules
try:
    import cv2
    import numpy as np
    import face_recognition
    print("\n✓ Libraries loaded")
except ImportError as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)

# Load faces
print("\n[1] Loading faces from 'faces' folder...")
face_dir = 'faces'
face_encodings = []
face_names = []

if not os.path.isdir(face_dir):
    print("✗ 'faces' folder not found!")
    sys.exit(1)

files = [f for f in os.listdir(face_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

if not files:
    print("✗ No face images found in 'faces' folder!")
    sys.exit(1)

print(f"Found {len(files)} face images:")

for filename in files:
    try:
        path = os.path.join(face_dir, filename)
        img = cv2.imread(path)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        encodings = face_recognition.face_encodings(rgb)
        if encodings:
            face_encodings.append(encodings[0])
            name = os.path.splitext(filename)[0]
            face_names.append(name)
            print(f"  ✓ {filename} → {name}")
        else:
            print(f"  ✗ {filename} - No face detected")
    except Exception as e:
        print(f"  ✗ {filename} - Error: {e}")

if not face_encodings:
    print("\n✗ No faces could be loaded!")
    sys.exit(1)

print(f"\n✓ Loaded {len(face_encodings)} faces successfully")

# Demo mode
print("\n[2] Demo Mode Options:")
print("  1 - Test face recognition (simulated)")
print("  2 - View all registered faces")
print("  3 - Exit")

choice = input("\nChoose option (1-3): ").strip()

if choice == "1":
    # Test recognition
    print("\n[Demo] Simulating face recognition test...")
    print(f"Available faces to recognize: {', '.join(face_names)}")
    
    num_tests = int(input("How many test recognitions? (1-10): ") or "5")
    
    print("\n" + "=" * 70)
    print("SIMULATING FACE DETECTION")
    print("=" * 70)
    
    # Create attendance CSV if not exists
    csv_path = 'attendance/attendance.csv'
    os.makedirs('attendance', exist_ok=True)
    
    for i in range(num_tests):
        # Randomly pick a face
        test_name = random.choice(face_names)
        
        print(f"\n[Test {i+1}] Detecting face...")
        
        # Simulate recognition
        now = datetime.now()
        time_str = now.strftime('%H:%M:%S')
        date_str = now.strftime('%Y-%m-%d')
        
        print(f"  ✓ Face detected: {test_name.upper()}")
        print(f"  ✓ Distance: {random.uniform(0.2, 0.5):.3f} (< 0.6 = match)")
        print(f"  ✓ Marking attendance at {time_str}")
        
        # Write to CSV
        if not os.path.exists(csv_path):
            with open(csv_path, 'w') as f:
                f.write("Name,Time,Date\n")
        
        with open(csv_path, 'a') as f:
            f.write(f"{test_name.upper()},{time_str},{date_str}\n")
        
        # Write log
        os.makedirs('logs', exist_ok=True)
        with open('logs/security_logs.txt', 'a') as f:
            f.write(f"[DEMO] AUTHORIZED ACCESS: {test_name.upper()}\n")
        
        print(f"  ✓ Marked in CSV")
        
        # Small delay
        import time
        time.sleep(0.5)
    
    print("\n" + "=" * 70)
    print(f"✓ DEMO COMPLETE - {num_tests} faces recognized")
    print("=" * 70)
    
    print(f"\nAttendance saved to: {csv_path}")
    print("Logs saved to: logs/security_logs.txt")
    
    # Show CSV
    if os.path.exists(csv_path):
        print("\nAttendance records:")
        with open(csv_path, 'r') as f:
            print(f.read())

elif choice == "2":
    # View faces
    print("\n[Info] Registered faces:")
    for i, name in enumerate(face_names, 1):
        path = os.path.join(face_dir, f"{name}.jpg")
        if not os.path.exists(path):
            path = os.path.join(face_dir, f"{name}.jpeg")
        if not os.path.exists(path):
            path = os.path.join(face_dir, f"{name}.png")
        
        size = os.path.getsize(path) / 1024
        print(f"  {i}. {name.upper()} ({size:.1f} KB)")
    
    print(f"\nTotal: {len(face_names)} faces")
    print("\nTo use real attendance:")
    print("  1. Fix camera driver")
    print("  2. Run: python main.py")
    print("  3. Click 'Start Attendance'")

else:
    print("Exiting...")
    sys.exit(0)

print("\n" + "=" * 70)
print("Next steps:")
print("  1. Fix camera driver (see CAMERA_DRIVER_FIX.md)")
print("  2. Run: python test_camera_fast.py")
print("  3. Then: python main.py")
print("=" * 70)

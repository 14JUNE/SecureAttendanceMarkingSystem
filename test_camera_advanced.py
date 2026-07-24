#!/usr/bin/env python3
"""
Advanced camera diagnostic - checks for camera availability and drivers
"""
import os
import sys
import subprocess

print("=" * 70)
print("ADVANCED CAMERA DIAGNOSTIC")
print("=" * 70)

# Step 1: Check Windows Device Manager for cameras
print("\n[Step 1] Checking Windows for cameras...")
try:
    # Query Windows for camera devices
    result = subprocess.run(
        ['Get-PnpDevice', '-Class', 'Camera', '-Status', 'OK'],
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print("✓ Found cameras in Windows:")
        print(result.stdout)
    else:
        print("⚠️  No cameras found in Windows Device Manager")
        print("\nNote: Camera might be:")
        print("  - Not connected")
        print("  - Disabled in Device Manager")
        print("  - Driver not installed")
        
except Exception as e:
    print(f"Could not query Device Manager: {e}")

# Step 2: Try OpenCV with different backends
print("\n[Step 2] Testing OpenCV with different backends...")
import cv2

backends = [
    (cv2.CAP_ANY, "ANY (Auto-detect)"),
    (cv2.CAP_DSHOW, "DSHOW (Windows)"),
    (cv2.CAP_VFW, "VFW (Legacy)"),
    (cv2.CAP_WINRT, "WINRT (Windows RT)"),
]

camera_found = False

for backend_id, backend_name in backends:
    print(f"\n  Trying {backend_name}...")
    try:
        # Try to open camera
        cap = cv2.VideoCapture(0, backend_id)
        
        if cap.isOpened():
            print(f"    ✓ Camera opened!")
            
            # Try to read frame
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"    ✓ Can read frames: {frame.shape}")
                camera_found = True
            else:
                print(f"    ⚠️  Camera open but can't read frames")
            
            cap.release()
            if camera_found:
                break
        else:
            print(f"    ✗ Camera not accessible with this backend")
            
    except Exception as e:
        print(f"    ✗ Error: {e}")

if not camera_found:
    print("\n⚠️  NO CAMERA FOUND")
    print("\nPossible solutions:")
    print("  1. Connect USB camera")
    print("  2. Check Device Manager for camera")
    print("  3. Update camera drivers")
    print("  4. Restart Windows")
    print("  5. Try different USB port")

# Step 3: Try different camera indices
print("\n[Step 3] Scanning for cameras at different indices...")
indices_found = []
for i in range(5):
    try:
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"  ✓ Camera found at index {i}: {frame.shape}")
                indices_found.append(i)
            cap.release()
    except:
        pass

if indices_found:
    print(f"\n✓ Camera available at indices: {indices_found}")
    print(f"  Use index {indices_found[0]} in code")
else:
    print("\n✗ No cameras found at any index")

# Step 4: Check OpenCV version
print("\n[Step 4] OpenCV information...")
print(f"  OpenCV version: {cv2.__version__}")

# Step 5: Try simple display test (if camera found)
if camera_found or indices_found:
    print("\n[Step 5] Testing window display...")
    try:
        cap = cv2.VideoCapture(indices_found[0] if indices_found else 0)
        ret, frame = cap.read()
        if ret and frame is not None:
            cv2.imshow('CAMERA TEST', frame)
            print("  ✓ Window created")
            print("  >> Window should appear on screen")
            print("  >> Waiting 2 seconds...")
            key = cv2.waitKey(2000)
            cv2.destroyAllWindows()
            print("  ✓ Window closed")
        cap.release()
    except Exception as e:
        print(f"  ✗ Window display error: {e}")

print("\n" + "=" * 70)
if camera_found or indices_found:
    print("✓ CAMERA DETECTED")
    print("\nYou should be able to use the system now.")
    print("Try: python main.py")
else:
    print("✗ NO CAMERA DETECTED")
    print("\nNext steps:")
    print("1. Check Device Manager (Win+X → Device Manager → Cameras)")
    print("2. Look for your camera device")
    print("3. If red X or warning: right-click → Update driver")
    print("4. If not listed: connect camera and restart Windows")
    print("5. Check camera permissions in Windows Settings")
    print("   (Settings → Privacy & Security → Camera)")
print("=" * 70)

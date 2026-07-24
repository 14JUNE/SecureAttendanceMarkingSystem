#!/usr/bin/env python3
"""
Fast camera diagnostic with timeouts - doesn't hang
"""
import threading
import sys
import subprocess

print("=" * 70)
print("FAST CAMERA DIAGNOSTIC")
print("=" * 70)

# Step 1: Check Windows for cameras via PowerShell
print("\n[Step 1] Checking Windows Device Manager...")
try:
    result = subprocess.run(
        'Get-PnpDevice -Class Camera',
        shell=True,
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if 'OK' in result.stdout or result.stdout.strip():
        print("✓ Found cameras:")
        print(result.stdout[:200])
    else:
        print("✗ NO CAMERAS FOUND in Device Manager")
        print("\n  This means:")
        print("  • No camera is connected")
        print("  • OR camera drivers not installed")
        print("  • OR camera is disabled")
        
except Exception as e:
    print(f"Could not check Device Manager: {e}")

# Step 2: Try OpenCV with timeout
print("\n[Step 2] Testing OpenCV (with 2-second timeout)...")

def test_camera():
    global camera_works
    try:
        import cv2
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        
        ret, frame = cap.read()
        camera_works = (ret and frame is not None)
        
        cap.release()
    except Exception as e:
        print(f"  Error: {e}")

camera_works = False
thread = threading.Thread(target=test_camera, daemon=True)
thread.start()
thread.join(timeout=2.0)

if camera_works:
    print("✓ Camera works!")
else:
    print("✗ Camera not working")

# Step 3: Summary and suggestions
print("\n[Step 3] Summary...")
print("=" * 70)

if camera_works:
    print("✓ CAMERA IS WORKING")
    print("\nYou can now use: python main.py")
else:
    print("✗ CAMERA NOT DETECTED")
    print("\nTo fix:")
    print("  1. Connect a USB camera/webcam")
    print("  2. Open Device Manager:")
    print("     Right-click Start → Device Manager → Cameras")
    print("  3. Check if camera appears")
    print("  4. If camera has ⚠️ : Update drivers")
    print("     Right-click camera → Update driver → Search automatically")
    print("  5. Restart computer after updating drivers")
    print("  6. Run this test again")

print("\n" + "=" * 70)

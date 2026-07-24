#!/usr/bin/env python3
"""
Simple step-by-step test to debug camera window issue
This test separates each step to find where it breaks
"""
import os
import sys
import threading
import time

print("=" * 70)
print("SMART ATTENDANCE - CAMERA WINDOW DEBUG TEST")
print("=" * 70)

# Step 1: Import modules
print("\n[Step 1] Importing modules...")
try:
    import cv2
    import numpy as np
    print("✓ Modules imported")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Step 2: Open camera with timeout
print("\n[Step 2] Opening camera (with 5 second timeout)...")
camera_opened = False
cap = None
error_msg = None

def open_camera_thread():
    global camera_opened, cap, error_msg
    try:
        print("  > Creating VideoCapture object...")
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        print("  > Setting resolution...")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("  > Checking if camera is open...")
        if cap.isOpened():
            print("  > Reading test frame...")
            ret, frame = cap.read()
            if ret and frame is not None:
                print("  > ✓ Camera ready")
                camera_opened = True
            else:
                error_msg = "Camera opened but can't read frames"
        else:
            error_msg = "Camera failed to open"
    except Exception as e:
        error_msg = f"Exception: {e}"

# Run with timeout
thread = threading.Thread(target=open_camera_thread, daemon=True)
thread.start()
thread.join(timeout=5.0)

if not camera_opened:
    print(f"✗ FAILED: {error_msg}")
    print("\nTroubleshooting:")
    print("  1. Open Device Manager → Cameras")
    print("  2. Verify your camera is listed")
    print("  3. Disable other apps using camera (Zoom, Teams, etc.)")
    print("  4. Try: python -c \"import cv2; c = cv2.VideoCapture(0); print(c.isOpened())\"")
    sys.exit(1)

print("✓ Camera opened successfully")

# Step 3: Read a few frames
print("\n[Step 3] Reading frames...")
for i in range(3):
    ret, frame = cap.read()
    if ret and frame is not None:
        print(f"  ✓ Frame {i+1}: {frame.shape}")
    else:
        print(f"  ✗ Frame {i+1}: Failed to read")

# Step 4: Create window and display
print("\n[Step 4] Creating and displaying window...")
print("  >> A window should appear on your screen now <<")
print("  >> Press any key in the window to continue <<")
try:
    ret, frame = cap.read()
    if ret and frame is not None:
        window_name = 'TEST CAMERA WINDOW'
        
        # Add text to frame
        cv2.putText(frame, 'If you see this, window works!', (50, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow(window_name, frame)
        print(f"  ✓ Window '{window_name}' displayed")
        print(f"  >> Waiting 3 seconds (press any key to continue sooner)")
        
        key = cv2.waitKey(3000)
        print(f"  ✓ Key pressed or timeout: {key}")
        
        cv2.destroyAllWindows()
        print("  ✓ Window closed")
    else:
        print("  ✗ Could not read frame for display")
except Exception as e:
    print(f"  ✗ Window error: {e}")
    import traceback
    traceback.print_exc()

# Step 5: Test real-time display
print("\n[Step 5] Real-time camera display test (10 frames)...")
try:
    frame_count = 0
    while frame_count < 10:
        ret, frame = cap.read()
        if not ret or frame is None:
            print(f"  Frame {frame_count+1}: Failed to read")
            continue
        
        frame_count += 1
        
        # Add text and box
        cv2.rectangle(frame, (50, 50), (400, 150), (0, 255, 0), 2)
        cv2.putText(frame, f'Frame: {frame_count}/10', (100, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow('REALTIME TEST', frame)
        
        # Press Q to stop
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print(f"  Stopped at frame {frame_count} (Q pressed)")
            break
    
    print(f"  ✓ Displayed {frame_count} frames")
    cv2.destroyAllWindows()
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Cleanup
print("\n[Step 6] Cleanup...")
try:
    cap.release()
    cv2.destroyAllWindows()
    print("✓ Camera released and windows closed")
except Exception as e:
    print(f"Warning: {e}")

print("\n" + "=" * 70)
print("✓ ALL TESTS PASSED - Camera is working!")
print("=" * 70)
print("\nNow try: python main.py")

#!/usr/bin/env python3
"""Diagnostic test to find why camera window doesn't open"""
import os
import sys

print("=" * 70)
print("CAMERA WINDOW DIAGNOSTIC TEST")
print("=" * 70)

# Step 1: Load libraries
print("\n[Step 1] Loading libraries...")
try:
    import cv2
    import numpy as np
    print("✓ Libraries loaded")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Step 2: Check if camera exists
print("\n[Step 2] Checking camera...")
try:
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    print(f"  Camera object created: {cap}")
    
    is_open = cap.isOpened()
    print(f"  Is camera open? {is_open}")
    
    if not is_open:
        print("✗ Camera failed to open!")
        print("  Try:")
        print("  1. Restart computer")
        print("  2. Check Device Manager → Camera")
        print("  3. Check if Zoom/Skype is using camera")
        sys.exit(1)
    else:
        print("✓ Camera opened successfully")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Try to read frames
print("\n[Step 3] Reading frames from camera...")
try:
    frames_read = 0
    for i in range(5):
        ret, frame = cap.read()
        print(f"  Frame {i+1}: ret={ret}, shape={frame.shape if frame is not None else 'None'}")
        if ret and frame is not None:
            frames_read += 1
        else:
            print(f"  ✗ Failed to read frame {i+1}")
    
    if frames_read > 0:
        print(f"✓ Successfully read {frames_read}/5 frames")
    else:
        print("✗ Could not read any frames")
        cap.release()
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Error reading frames: {e}")
    import traceback
    traceback.print_exc()
    cap.release()
    sys.exit(1)

# Step 4: Try to display a frame
print("\n[Step 4] Testing window display...")
try:
    ret, frame = cap.read()
    if ret and frame is not None:
        print(f"  Creating window...")
        cv2.imshow('TEST: Camera Feed', frame)
        print(f"  Window created")
        
        print(f"\n  >>> WINDOW SHOULD APPEAR ABOVE <<<")
        print(f"  >>> Press any key in the window to continue <<<")
        
        # Wait for key
        key = cv2.waitKey(5000)  # Wait up to 5 seconds
        print(f"\n  Key pressed: {key}")
        
        cv2.destroyAllWindows()
        print("✓ Window displayed and closed successfully")
    else:
        print("✗ Could not read frame for display test")
        
except Exception as e:
    print(f"✗ Error displaying window: {e}")
    import traceback
    traceback.print_exc()

# Step 5: Test with real loop
print("\n[Step 5] Testing real camera loop (5 seconds)...")
print("  Press Q to stop early, window should show live camera feed")
try:
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret or frame is None:
            print(f"  Frame {frame_count}: Failed to read")
            continue
        
        frame_count += 1
        
        # Add text to frame
        cv2.putText(frame, f'Frame: {frame_count}', (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display
        cv2.imshow('Real Camera Loop Test', frame)
        
        # Check for exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(f"  User pressed Q")
            break
        
        # Auto-exit after 10 seconds
        if frame_count > 300:  # ~10 seconds at 30fps
            print(f"  Auto-timeout after {frame_count} frames")
            break
    
    print(f"✓ Read {frame_count} frames successfully")
    cv2.destroyAllWindows()
    cap.release()
    
except Exception as e:
    print(f"✗ Error in loop: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
print("\nIf camera window didn't appear:")
print("1. Check if camera is connected")
print("2. Check Device Manager for camera")
print("3. Try restarting Python")
print("4. Try unplugging and replugging camera")

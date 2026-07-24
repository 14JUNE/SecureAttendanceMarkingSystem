#!/usr/bin/env python3
"""
Comprehensive camera diagnostic - finds why camera won't work even with drivers installed
"""
import os
import sys
import subprocess
import threading
import time

print("=" * 70)
print("CAMERA TROUBLESHOOTING - DRIVER INSTALLED BUT NOT WORKING")
print("=" * 70)

# Step 1: Verify camera appears in Device Manager
print("\n[Step 1] Checking Device Manager...")
try:
    result = subprocess.run(
        'Get-PnpDevice -Class Camera -Status OK',
        shell=True,
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.stdout.strip():
        print("✓ Camera IS recognized by Windows")
        print(result.stdout[:300])
    else:
        print("⚠️  Camera not showing as OK in Device Manager")
        # Try to find any camera
        result2 = subprocess.run(
            'Get-PnpDevice -Class Camera',
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result2.stdout.strip():
            print("  But found camera devices:")
            print(result2.stdout[:300])
        
except Exception as e:
    print(f"Could not check Device Manager: {e}")

# Step 2: Check Windows Camera app
print("\n[Step 2] Checking if Windows Camera app can access camera...")
print("  (If Camera app works, then Python permission issue)")
print("  → Open Windows Camera app and test")
print("  → Tell me if it works there")

# Step 3: Check Windows Privacy Settings
print("\n[Step 3] Checking Windows Privacy & Security...")
try:
    result = subprocess.run(
        'Get-ChildItem "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\camera" -ErrorAction SilentlyContinue',
        shell=True,
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if 'camera' in result.stdout.lower():
        print("✓ Camera privacy settings found")
    else:
        print("⚠️  Could not verify camera privacy settings")
        
except Exception as e:
    print(f"Could not check privacy settings: {e}")

# Step 4: Check if other apps are using camera
print("\n[Step 4] Checking for apps using camera...")
try:
    result = subprocess.run(
        'Get-Process | Where-Object {$_.Name -like "*zoom*" -or $_.Name -like "*teams*" -or $_.Name -like "*skype*" -or $_.Name -like "*obs*"}',
        shell=True,
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.stdout.strip():
        print("⚠️  Found apps that might use camera:")
        print(result.stdout)
        print("\n  ⚠️  CLOSE THESE APPS first!")
        print("  These apps might have exclusive access to camera:")
        print("    • Zoom")
        print("    • Teams")
        print("    • Skype")
        print("    • Discord")
        print("    • OBS")
        print("    • Any other video conferencing software")
    else:
        print("✓ No obvious apps using camera")
        
except Exception as e:
    print(f"Could not check running apps: {e}")

# Step 5: Check BIOS settings (camera might be disabled in BIOS)
print("\n[Step 5] Checking if camera is disabled in BIOS...")
print("  This is common on laptops. To check:")
print("  1. Restart computer")
print("  2. During startup, press:")
print("     • F2 or F10 (Dell)")
print("     • DEL (HP, ASUS, MSI)")
print("     • F12 (Lenovo)")
print("  3. Look for 'Integrated Peripherals' or 'Onboard Devices'")
print("  4. Find 'Camera', 'Webcam', or 'Integrated Camera'")
print("  5. Set to ENABLED")
print("  6. Save and exit")
print("  7. Run this test again")

# Step 6: Test OpenCV with timeout (doesn't hang)
print("\n[Step 6] Testing OpenCV camera access (with timeout)...")

camera_result = None

def test_opencv():
    global camera_result
    try:
        import cv2
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        # Set very low resolution to speed up
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
        
        if cap.isOpened():
            ret, frame = cap.read()
            camera_result = (ret and frame is not None)
        
        cap.release()
    except Exception as e:
        print(f"  Error: {e}")

thread = threading.Thread(target=test_opencv, daemon=True)
thread.start()
thread.join(timeout=3.0)

if camera_result is True:
    print("✓ OpenCV can access camera!")
elif camera_result is False:
    print("✗ Camera exists but OpenCV can't read frames")
    print("  Possible causes:")
    print("    • Camera is in use by another app")
    print("    • Camera needs permissions (Windows 11)")
    print("    • Camera disabled in BIOS")
    print("    • USB camera not properly connected")
else:
    print("✗ OpenCV timed out - camera might be very slow or frozen")

# Step 7: Detailed troubleshooting
print("\n" + "=" * 70)
print("TROUBLESHOOTING CHECKLIST")
print("=" * 70)

print("\n[ ] 1. Close all apps that use camera:")
print("      • Zoom")
print("      • Microsoft Teams")
print("      • Skype")
print("      • Discord")
print("      • OBS")
print("      • Browser tabs with webcam (Zoom, Meet, etc.)")

print("\n[ ] 2. Check Windows Privacy Settings:")
print("      • Settings → Privacy & Security → Camera")
print("      • Toggle OFF then ON")
print("      • Restart computer")

print("\n[ ] 3. Check BIOS (if laptop):")
print("      • Restart and enter BIOS")
print("      • Look for Integrated Camera")
print("      • Set to ENABLED")
print("      • Save and restart")

print("\n[ ] 4. Reinstall camera driver:")
print("      • Device Manager → Cameras")
print("      • Right-click camera")
print("      • Uninstall device")
print("      • Check: Delete driver software")
print("      • Uninstall")
print("      • Restart Windows")
print("      • Windows will auto-install drivers")

print("\n[ ] 5. Test with Windows Camera app:")
print("      • Click Start")
print("      • Type 'Camera'")
print("      • Open Camera app")
print("      • If it works: Python permission issue")
print("      • If it doesn't work: Hardware issue")

print("\n[ ] 6. Try different camera index:")
print("      • Edit attendence.py")
print("      • Change: cap = cv2.VideoCapture(0)")
print("      • To: cap = cv2.VideoCapture(1)")
print("      • Or: cap = cv2.VideoCapture(2)")

print("\n" + "=" * 70)
print("QUICK ACTION PLAN")
print("=" * 70)

print("\n1. Close ALL apps that use camera")
print("2. Restart Windows completely")
print("3. Run: python test_camera_fast.py")
print("4. Tell me the exact error message")

print("\n" + "=" * 70)

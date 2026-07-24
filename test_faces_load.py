#!/usr/bin/env python3
"""Test if faces are loading correctly"""
import os
import sys

print("=" * 60)
print("FACE LOADING TEST")
print("=" * 60)

print(f"\n[1] Working directory: {os.getcwd()}")
print(f"[2] Faces folder exists: {os.path.isdir('faces')}")

if os.path.isdir('faces'):
    files = os.listdir('faces')
    print(f"[3] Files in faces/: {files}")
else:
    print("[3] ERROR: faces folder not found!")
    sys.exit(1)

print(f"\n[4] Importing attendence module...")
try:
    from SmartAttendence import attendence
    print("    ✓ Import successful")
except Exception as e:
    print(f"    ✗ Import failed: {e}")
    sys.exit(1)

print(f"\n[5] Loading known faces...")
try:
    attendence.load_known_faces()
    print(f"    ✓ Loaded {len(attendence.encodeListKnown)} faces")
    print(f"    Names: {attendence.classNames}")
except Exception as e:
    print(f"    ✗ Failed to load faces: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if len(attendence.encodeListKnown) == 0:
    print("\n⚠️  WARNING: No faces loaded!")
    print("    This could mean:")
    print("    - Face images are corrupted")
    print("    - No valid faces detected in images")
    print("    - Image format not supported (.jpg, .jpeg, .png)")
else:
    print(f"\n✓ SUCCESS: {len(attendence.encodeListKnown)} faces ready for recognition")

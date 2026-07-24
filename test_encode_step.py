#!/usr/bin/env python3
"""Direct face encoding test with step-by-step output"""
import os
import sys

print("Testing face encodings step by step...\n")

# Import libraries
print("[Loading libraries...]")
import cv2
import face_recognition
print("✓ Libraries loaded\n")

# Check each file
face_dir = 'faces'
files = [f for f in os.listdir(face_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
print(f"Found {len(files)} images:\n")

success_count = 0
for filename in files:
    path = os.path.join(face_dir, filename)
    print(f"Processing: {filename}")
    
    try:
        # Step 1: Read image
        img = cv2.imread(path)
        print(f"  ✓ Read image: {img.shape}")
        
        # Step 2: Convert to RGB
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        print(f"  ✓ Converted to RGB")
        
        # Step 3: Detect faces
        locations = face_recognition.face_locations(rgb)
        print(f"  ✓ Found {len(locations)} face(s)")
        
        # Step 4: Encode
        if locations:
            encodings = face_recognition.face_encodings(rgb, locations)
            print(f"  ✓ Created {len(encodings)} encoding(s)")
            success_count += 1
        else:
            print(f"  ⚠️  No faces detected")
            
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print()

print(f"Summary: {success_count}/{len(files)} faces successfully encoded")
if success_count == len(files):
    print("✓ All faces ready!")
else:
    print("⚠️  Some faces failed - check above for errors")

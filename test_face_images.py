#!/usr/bin/env python3
"""Quick test to check if each face image can be loaded"""
import os
import sys
sys.path.insert(0, '.')

print("=" * 60)
print("QUICK FACE VERIFICATION TEST")
print("=" * 60)

# Step 1: Check files exist
faces_dir = 'faces'
if not os.path.isdir(faces_dir):
    print(f"❌ ERROR: {faces_dir} directory not found!")
    sys.exit(1)

files = [f for f in os.listdir(faces_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
print(f"\n✓ Found {len(files)} face images:")
for f in files:
    full_path = os.path.join(faces_dir, f)
    size = os.path.getsize(full_path)
    print(f"  - {f} ({size} bytes)")

# Step 2: Try loading OpenCV  
print("\n[Loading OpenCV...]")
try:
    import cv2
    print("✓ OpenCV loaded")
except Exception as e:
    print(f"❌ OpenCV failed: {e}")
    sys.exit(1)

# Step 3: Try loading face_recognition
print("[Loading face_recognition...]")
try:
    import face_recognition
    print("✓ face_recognition loaded (this may take 30-60 seconds on first run)")
except Exception as e:
    print(f"❌ face_recognition failed: {e}")
    sys.exit(1)

# Step 4: Try reading each image with OpenCV
print("\n[Reading images with OpenCV...]")
for filename in files:
    image_path = os.path.join(faces_dir, filename)
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"  ❌ {filename}: Could not read (might be corrupted)")
        else:
            print(f"  ✓ {filename}: {img.shape[0]}x{img.shape[1]} pixels")
    except Exception as e:
        print(f"  ❌ {filename}: {e}")

# Step 5: Try encoding faces
print("\n[Encoding faces (this takes time - be patient)...]")
for filename in files:
    image_path = os.path.join(faces_dir, filename)
    try:
        # Read and convert
        img = cv2.imread(image_path)
        if img is None:
            print(f"  ❌ {filename}: Cannot read")
            continue
        
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Try to detect faces
        print(f"  > {filename}: Detecting faces...")
        faces = face_recognition.face_locations(rgb_img)
        print(f"    Found {len(faces)} face(s)")
        
        if faces:
            encodings = face_recognition.face_encodings(rgb_img, faces)
            if encodings:
                print(f"    ✓ Created {len(encodings)} encoding(s)")
            else:
                print(f"    ❌ Could not create encoding")
        else:
            print(f"    ⚠️  No faces detected in {filename}")
            
    except Exception as e:
        print(f"  ❌ {filename}: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)

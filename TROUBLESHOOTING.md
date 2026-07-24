# Attendance System Troubleshooting Guide

## If "Start Attendance" is not working

Follow these steps to diagnose and fix the issue:

### Step 1: Run the Diagnostic Test
```bash
python test_minimal.py
```

This test checks:
- ✓ Faces folder exists with images
- ✓ All libraries are installed
- ✓ Face detection works
- ✓ Camera is working

**If test fails at any step:** Follow the specific fix below

---

## Common Issues & Fixes

### ❌ "No face images in faces/ folder"

**Problem:** Faces folder is empty

**Fix:**
1. Create `.jpg` or `.png` images of people's faces
2. Save to the `faces/` folder
3. Use format: `firstname_lastname.jpg`
   - Example: `john_doe.jpg`, `jane_smith.jpg`
4. **Requirements:**
   - Clear, frontal face photos
   - Good lighting (no shadows on face)
   - Face fills at least 30% of image
   - One face per image (or one main face)

**Test:**
```bash
python test_minimal.py
```

---

### ❌ "Missing library" errors

**Problem:** A Python package is not installed

**Fix:**
```bash
pip install opencv-python face-recognition dlib-bin numpy pandas
```

Then test again:
```bash
python test_minimal.py
```

---

### ❌ "Camera not accessible"

**Problem:** Camera cannot be opened

**Fix:**
1. **Check camera is connected**
   - Plug in USB camera if using external camera

2. **Close other applications using camera**
   - Close Zoom, Teams, Discord, etc.
   - These programs lock the camera

3. **Check Windows permissions**
   - Settings → Privacy & Security → Camera
   - Enable camera access for Python

4. **Try USB camera instead of built-in**
   - Some laptops have broken built-in cameras

5. **Restart camera service (Windows)**
   ```powershell
   # Run as Administrator:
   Get-Service -Name "Wcmsvc" | Restart-Service
   ```

---

### ❌ "No faces detected in frames"

**Problem:** Face detection isn't working even with camera on

**Fix:**
1. **Improve lighting**
   - Use front-facing light (not backlit)
   - Avoid harsh shadows
   - Use 60-100W equivalent light bulb

2. **Move closer to camera**
   - Face should fill most of the video frame
   - Try 12-18 inches from camera

3. **Face detection too strict**
   - Edit `attendence.py` line ~192:
   ```python
   distance_threshold = 0.6  # Try 0.7 for more lenient
   ```

4. **Test the detection separately**
   ```bash
   python test_attendance.py
   ```

---

### ❌ "Attendance not recording"

**Problem:** Faces are detected but not marked as attendance

**Fix:**
1. **Check if faces are recognized**
   - When you see a green box + name = working!
   - When you see "UNKNOWN" = face not in database

2. **Add matching face image**
   - If showing "UNKNOWN", you need to add that person's face to `faces/` folder

3. **Check blink detection (anti-spoofing)**
   - If "SPOOF DETECTED" shows, blink in front of camera
   - The system requires eye movement to confirm real person

4. **Check file permissions**
   - Ensure `attendance/` folder exists and is writable
   - Run: `python test_minimal.py`

5. **Check logs**
   - Open: `logs/security_logs.txt`
   - Should show "AUTHORIZED ACCESS" if working

---

### ❌ "Camera shows but face window frozen"

**Problem:** Window won't update or closes immediately

**Fix:**
1. **Press Q key to close**
   - The window requires Q key press to close
   - Don't click the close button

2. **Check terminal output**
   - Error messages appear in terminal/console
   - Read error messages carefully

3. **Check face detection timeout**
   - Face detection can be slow on first run
   - Wait 10-15 seconds for first detection

---

### ❌ "Email alerts not working"

**Problem:** Unknown person detected but email not sent

**Fix:**
1. **Check email configuration**
   - Edit `email_alert.py`
   - Verify `sender_email` and `receiver_email`

2. **Get Gmail app password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Copy 16-character password (remove spaces)
   - Paste in `email_alert.py` as `sender_password`

3. **Check firewall**
   - SMTP port 465 must be open
   - Antivirus might be blocking SMTP
   - Try disabling firewall temporarily to test

4. **Check internet**
   - Ping Google: `ping google.com`
   - SMTP requires internet connection

---

## Debug Steps

### 1. Check console output
When running `python main.py`:
- Look at the terminal window
- Error messages show there
- Don't close terminal until done testing

### 2. Check log files
```
logs/security_logs.txt     → All access attempts
attendance/attendance.csv  → Attendance records
```

### 3. Enable verbose output
Edit `attendence.py` and add more print statements:
```python
print(f"Face detected: {len(facesCurFrame)} faces")
print(f"Known faces loaded: {len(encodeListKnown)}")
print(f"Match distance: {distance}")
```

### 4. Test step by step

**Test 1: Can Python find the modules?**
```bash
python -c "import cv2; import face_recognition; print('OK')"
```

**Test 2: Can module load?**
```bash
python -c "import attendence; print('OK')"
```

**Test 3: Can faces load?**
```bash
python -c "import attendence; attendence.load_known_faces(); print(len(attendence.encodeListKnown))"
```

**Test 4: Can camera open?**
```bash
python test_minimal.py
```

**Test 5: Full system**
```bash
python main.py
```

---

## When to Ask for Help

Include:
1. **Error message** (exact text from console)
2. **What you see** (no window? frozen? wrong output?)
3. **What you did** (added faces? changed settings?)
4. **System info:**
   ```bash
   python --version
   ```

---

## Quick Reference

| Issue | Fix |
|-------|-----|
| No faces folder | Create `faces/` and add `.jpg` files |
| Camera not working | Close other apps, check permissions |
| Face not detected | Move closer, improve lighting |
| Attendance not recording | Check `logs/security_logs.txt` |
| Email not working | Verify credentials, check firewall |
| Program crashes | Check console, read error message |
| Face not recognized | Add more images of that person |

---

## Getting Started Again

1. **Add face images**
   ```
   faces/john_doe.jpg
   faces/jane_smith.jpg
   ```

2. **Run test**
   ```bash
   python test_minimal.py
   ```

3. **Start system**
   ```bash
   python main.py
   ```

4. **Login**
   - Username: `admin`
   - Password: `1234`

5. **Click "Start Attendance"**
   - Look at camera
   - See your name with green box = working!
   - Press Q to stop

---

**Still having issues?** Run all tests and share the output:
```bash
python test_minimal.py
python test_attendance.py
python test_setup.py
```

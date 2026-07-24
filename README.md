# Smart Attendance System

A face recognition-based attendance system with anti-spoofing protection and email alerts.

## Quick Start

### 1. First-Time Setup
Run the diagnostic test to check if everything is installed:
```bash
python test_setup.py
```

### 2. Add Face Images
1. Create `.jpg` or `.png` images of people's faces
2. Save them to the `faces/` folder
3. Use format: `firstname_lastname.jpg`
   - Example: `john_doe.jpg`, `jane_smith.jpg`
4. Clear, well-lit faces work best

### 3. Run the System
```bash
python main.py
```

1. Login with credentials: **admin / 1234**
2. Click "Start Attendance"
3. Press **Q** to stop

## What Works

### ✅ Face Recognition
- Real-time detection from webcam
- Matches against registered faces
- Supports multiple people

### ✅ Attendance Tracking
- Records name, time, date
- Saves to `attendance/attendance.csv`
- One entry per person per day

### ✅ Security
- Unknown person detection
- Screenshot capture: `screenshots/`
- Email alerts (optional)
- Security logging: `logs/security_logs.txt`

### ✅ Anti-Spoofing
- Blink detection to prevent photo attacks
- Rejects spoof attempts

## Configuration

### Email Alerts (Optional)
Edit `email_alert.py` to enable alerts:

```python
sender_email = "your_email@gmail.com"
sender_password = "your_app_password"  # From Google Account
receiver_email = "alert_recipient@gmail.com"
```

**To get Gmail app password:**
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Copy the 16-character password

## Directory Structure

```
SmartAttendence/
├── faces/              # Add face images here
├── attendance/         # attendance.csv (records)
├── logs/              # security_logs.txt
├── screenshots/       # Unknown person captures
├── main.py            # Run this
├── test_setup.py      # Run this first
└── CONFIG.md          # Detailed documentation
```

## Troubleshooting

### "No registered faces found"
- Add .jpg/.png files to `faces/` folder
- Use format: `name.jpg`
- Ensure faces are clearly visible

### Camera not detected
- Check camera is connected
- Close other video apps (Zoom, Teams, etc.)
- Allow camera permissions in Windows

### Attendance not recording
- Check faces folder has images
- Ensure clear lighting
- Check logs/security_logs.txt for errors

### Email not sending
- Verify app password is set correctly
- Check internet connection
- Allow SMTP port 465 through firewall

## File Locations

- **Attendance records**: `attendance/attendance.csv`
- **Security logs**: `logs/security_logs.txt`
- **Unknown faces**: `screenshots/unknown_*.jpg`
- **Configuration**: Edit `email_alert.py` for email setup

## Default Credentials

- Username: **admin**
- Password: **1234**

*Change these in `login.py` for production*

## System Requirements

- Windows 10/11
- Python 3.12+
- Webcam
- 500MB+ free space
- 4GB RAM recommended

## Need Help?

1. Run `python test_setup.py` to diagnose issues
2. Check `logs/security_logs.txt` for error messages
3. Look at console output for detailed debugging
4. Read `CONFIG.md` for advanced setup

---

**Built with**: OpenCV, face_recognition, NumPy, Pandas, Tkinter

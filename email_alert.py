"""
Email utilities for Smart Attendance System:
1. Send alert to admin when someone enters wrong code (malicious attempt)
2. Alert on unknown person detection
"""
import smtplib
from email.message import EmailMessage

# ===== CONFIGURE YOUR EMAIL HERE =====
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_16_char_app_password"  # App password (not Gmail password)

# ===== ADMIN EMAIL =====
# All security alerts go here
ADMIN_EMAIL = "admin@example.com"  # Change to admin's email


def send_email_alert(image_path):
    """Send alert email when an unknown person is detected"""
    msg = EmailMessage()
    msg['Subject'] = 'UNKNOWN PERSON DETECTED - Smart Attendance'
    msg['From'] = SENDER_EMAIL
    msg['To'] = ADMIN_EMAIL

    msg.set_content('An unidentified person was detected at the attendance camera.')

    with open(image_path, 'rb') as f:
        file_data = f.read()
        file_name = f.name

    msg.add_attachment(file_data,
                       maintype='image',
                       subtype='jpeg',
                       filename=file_name)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        print(f"[EMAIL] Alert sent to admin (unknown person)")
        return True
    except Exception as e:
        # Don't spam console - only first failure
        if not hasattr(send_email_alert, '_warned'):
            send_email_alert._warned = True
            print(f"[EMAIL] Cannot send alerts: {e}")
            print("  To fix: Update SENDER_EMAIL/PASSWORD in email_alert.py")
        return False


def send_malicious_alert(name, image_path, wrong_code):
    """
    Send alert when someone enters a wrong verification code.
    
    Args:
        name: The student name that was spoofed
        image_path: Path to the captured screenshot
        wrong_code: The incorrect code that was entered
    """
    msg = EmailMessage()
    msg['Subject'] = f'SECURITY ALERT - Spoof attempt for {name}'
    msg['From'] = SENDER_EMAIL
    msg['To'] = ADMIN_EMAIL

    msg.set_content(
        f"SECURITY INCIDENT\n\n"
        f"Someone attempted to mark attendance for: {name}\n"
        f"Wrong code entered: {wrong_code}\n"
        f"Time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"Photo of the person at camera is attached.\n"
        f"This may be a spoofing attempt using a photo or video.\n"
        f"Please investigate immediately."
    )

    with open(image_path, 'rb') as f:
        file_data = f.read()
        file_name = f.name

    msg.add_attachment(file_data,
                       maintype='image',
                       subtype='jpeg',
                       filename=file_name)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        print(f"[EMAIL] SECURITY ALERT sent to admin for {name}")
        return True
    except Exception as e:
        if not hasattr(send_malicious_alert, '_warned'):
            send_malicious_alert._warned = True
            print(f"[EMAIL] Cannot send security alert: {e}")
        return False


def send_registration_notification(student_data):
    """
    Send notification to admin when a new student registers.
    
    Args:
        student_data: dict with keys: name, email, class, face_file, registered_on
    """
    msg = EmailMessage()
    msg['Subject'] = f'NEW STUDENT REGISTRATION - {student_data["name"]}'
    msg['From'] = SENDER_EMAIL
    msg['To'] = ADMIN_EMAIL

    msg.set_content(
        f"NEW STUDENT REGISTRATION\n\n"
        f"Name: {student_data['name']}\n"
        f"Email: {student_data['email']}\n"
        f"Class: {student_data['class']}\n"
        f"Face File: {student_data['face_file']}\n"
        f"Registered: {student_data['registered_on']}\n\n"
        f"The student's face has been added to the attendance system.\n"
        f"Please verify the details if needed."
    )

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        print(f"[EMAIL] Registration notification sent to admin for {student_data['name']}")
        return True
    except Exception as e:
        if not hasattr(send_registration_notification, '_warned'):
            send_registration_notification._warned = True
            print(f"[EMAIL] Cannot send registration notification: {e}")
        return False


def send_student_alert(student_email, student_name, incident_type, details=""):
    """
    Send alert to a student about suspicious activity on their account.
    
    Args:
        student_email: Student's email address
        student_name: Student's name
        incident_type: Type of incident (e.g., "Wrong code attempt", "Spoof attempt")
        details: Additional details about the incident
    """
    msg = EmailMessage()
    msg['Subject'] = f'ALERT - Suspicious Activity on Your Attendance Account'
    msg['From'] = SENDER_EMAIL
    msg['To'] = student_email

    msg.set_content(
        f"Dear {student_name},\n\n"
        f"This is an automated alert from the Smart Attendance System.\n\n"
        f"Incident: {incident_type}\n"
        f"Time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"{details}\n\n"
        f"Someone attempted to mark attendance using your identity.\n"
        f"If this was not you, please contact the admin immediately.\n\n"
        f"Regards,\nSmart Attendance System"
    )

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        print(f"[EMAIL] Alert sent to student {student_name} at {student_email}")
        return True
    except Exception as e:
        if not hasattr(send_student_alert, '_warned'):
            send_student_alert._warned = True
            print(f"[EMAIL] Cannot send student alert: {e}")
        return False


# ===== THREADED EMAIL WRAPPERS (non-blocking, real-time) =====

def _email_worker(target_func, args, kwargs):
    """Run an email function in a background thread so the main thread is never blocked."""
    import threading as _threading
    thread = _threading.Thread(target=target_func, args=args, kwargs=kwargs, daemon=True)
    thread.start()


def send_email_alert_threaded(image_path):
    """Non-blocking version of send_email_alert - runs in background thread."""
    _email_worker(send_email_alert, (image_path,), {})


def send_malicious_alert_threaded(name, image_path, wrong_code):
    """Non-blocking version of send_malicious_alert - runs in background thread."""
    _email_worker(send_malicious_alert, (name, image_path, wrong_code), {})


def send_registration_notification_threaded(student_data):
    """Non-blocking version of send_registration_notification - runs in background thread."""
    _email_worker(send_registration_notification, (student_data,), {})


def send_student_alert_threaded(student_email, student_name, incident_type, details=""):
    """Non-blocking version of send_student_alert - runs in background thread."""
    _email_worker(send_student_alert, (student_email, student_name, incident_type, details), {})

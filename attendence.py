import os
import csv
import shutil
import numpy as np
from datetime import datetime
import threading
import time as _time

cv2 = None
face_recognition = None

_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR = os.path.dirname(_MODULE_DIR)
if os.path.exists(os.path.join(_PARENT_DIR, 'gui.py')):
    PROJECT_DIR = _PARENT_DIR
else:
    PROJECT_DIR = _MODULE_DIR


def _project_path(*parts):
    return os.path.join(PROJECT_DIR, *parts)


for directory in ['faces', 'attendance', 'logs', 'screenshots', 'unknown']:
    os.makedirs(_project_path(directory), exist_ok=True)

try:
    from email_alert import send_email_alert_threaded, send_malicious_alert_threaded, send_student_alert_threaded
except ImportError:
    from SmartAttendence.email_alert import send_email_alert_threaded, send_malicious_alert_threaded, send_student_alert_threaded

try:
    from anti_spoof import detect_blink
except ImportError:
    from SmartAttendence.anti_spoof import detect_blink

try:
    from student_registration import find_student_by_face, cleanup_orphaned_students, get_student_email
except ImportError:
    from SmartAttendence.student_registration import find_student_by_face, cleanup_orphaned_students, get_student_email

path = _project_path('faces')
images = []
classNames = []
encodeListKnown = []


def _load_libraries():
    global cv2, face_recognition
    if cv2 is None:
        print("Loading computer vision libraries...")
        import cv2 as cv2_lib
        import face_recognition as face_rec
        cv2 = cv2_lib
        face_recognition = face_rec
    return cv2, face_recognition


def load_known_faces():
    global images, classNames, encodeListKnown
    cv2_lib, face_rec = _load_libraries()
    images = []
    classNames = []
    encodeListKnown = []
    # Auto-clean orphaned student records whose face files are missing
    try:
        cleanup_orphaned_students()
    except:
        pass
    try:
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
            return
        for filename in os.listdir(path):
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            image_path = os.path.join(path, filename)
            current_img = cv2_lib.imread(image_path)
            if current_img is None:
                print(f"Warning: Could not read {filename}")
                continue
            rgb_img = cv2_lib.cvtColor(current_img, cv2_lib.COLOR_BGR2RGB)
            encodings = face_rec.face_encodings(rgb_img)
            if not encodings:
                print(f"Warning: No face found in {filename}")
                continue
            images.append(current_img)
            classNames.append(os.path.splitext(filename)[0])
            encodeListKnown.append(encodings[0])
        if encodeListKnown:
            print(f"Loaded {len(encodeListKnown)} known faces: {classNames}")
        else:
            print("No valid face encodings found in faces/ directory")
    except Exception as e:
        print(f"Error loading faces: {e}")


ATTENDANCE_COLUMNS = ['SessionID', 'StudentID', 'Name', 'Date', 'Time']
_attendance_file = _project_path('attendance', 'attendance.csv')
_attendance_running = False
_active_session_id = None
_session_marked_keys = set()
_session_counter = 0


def _attendance_mark_key(name, student_id):
    sid = str(student_id or '').strip()
    if sid:
        return f"id:{sid}"
    return f"name:{(name or '').upper()}"


def _session_number_from_id(session_id):
    text = str(session_id or '').strip()
    if not text.lower().startswith('session-'):
        return 0
    try:
        return int(text.split('-', 1)[1])
    except ValueError:
        return 0


def _next_attendance_session_id():
    global _session_counter
    highest = _session_counter

    file_path = _attendance_file
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    highest = max(highest, _session_number_from_id(row.get('SessionID', '')))
        except Exception as e:
            print(f"[WARN] Could not read previous sessions: {e}")

    _session_counter = highest + 1
    return f"Session-{_session_counter}"


def _begin_attendance_session(session_id):
    global _active_session_id, _session_marked_keys
    _active_session_id = session_id
    _session_marked_keys = set()
    write_log(f"SESSION START: {session_id}")


def _end_attendance_session():
    global _active_session_id, _session_marked_keys
    if _active_session_id:
        write_log(f"SESSION END: {_active_session_id}")
    _active_session_id = None
    _session_marked_keys = set()


def _is_marked_in_active_session(name, student_id, session_id):
    if session_id != _active_session_id:
        return False
    return _attendance_mark_key(name, student_id) in _session_marked_keys


def _record_session_mark(name, student_id, session_id):
    if session_id == _active_session_id:
        _session_marked_keys.add(_attendance_mark_key(name, student_id))


def _attendance_file_writable(file_path):
    os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
    try:
        with open(file_path, 'a', encoding='utf-8', newline=''):
            pass
        return True
    except PermissionError:
        return False


def prepare_attendance_file():
    """Pick a CSV file we can append to for this attendance session."""
    global _attendance_file
    candidates = [
        _project_path('attendance', 'attendance.csv'),
        _project_path('attendance', 'attendance_records.csv'),
    ]
    for file_path in candidates:
        if _attendance_file_writable(file_path):
            _attendance_file = file_path
            if file_path != candidates[0]:
                print(f"[WARN] {candidates[0]} is locked. Saving to {file_path} instead.")
            return file_path
    return None


def _backup_attendance_csv(file_path):
    backup_path = file_path + '.bak'
    if not os.path.exists(backup_path):
        shutil.copy2(file_path, backup_path)
        return backup_path

    counter = 1
    while True:
        backup_path = f"{file_path}.bak.{counter}"
        if not os.path.exists(backup_path):
            shutil.copy2(file_path, backup_path)
            return backup_path
        counter += 1


def _normalize_attendance_date(value):
    date_text = str(value or '').strip()
    for date_format in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y', '%d-%m-%Y'):
        try:
            return datetime.strptime(date_text, date_format).strftime('%Y-%m-%d')
        except ValueError:
            pass
    return date_text


def _migrate_attendance_csv(file_path):
    """Upgrade old CSV files and remove blank rows."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return

    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return
        old_rows = list(reader)

    current_layout = all(column in reader.fieldnames for column in ATTENDANCE_COLUMNS)
    has_blank_rows = any(not any(str(value or '').strip() for value in row.values()) for row in old_rows)
    has_non_iso_dates = any(
        _normalize_attendance_date(row.get('Date', '')) != str(row.get('Date', '') or '').strip()
        for row in old_rows
        if str(row.get('Date', '') or '').strip()
    )
    if current_layout and not has_blank_rows and not has_non_iso_dates:
        return

    _backup_attendance_csv(file_path)
    migrated = []
    for row in old_rows:
        if not any(str(value or '').strip() for value in row.values()):
            continue
        date = _normalize_attendance_date(row.get('Date', ''))
        time = row.get('Time', '')
        migrated.append({
            'SessionID': row.get('SessionID') or f"legacy_{date}_{time}".replace(':', '').replace('-', ''),
            'StudentID': row.get('StudentID', ''),
            'Name': row.get('Name', ''),
            'Date': date,
            'Time': time,
        })

    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=ATTENDANCE_COLUMNS)
        writer.writeheader()
        writer.writerows(migrated)
    print(f"[INFO] Migrated attendance file to new format ({len(migrated)} old records kept)")


def markAttendance(name, student_id="", session_id=""):
    file_path = _attendance_file
    try:
        os.makedirs(_project_path('attendance'), exist_ok=True)
        _migrate_attendance_csv(file_path)

        name = str(name or '').strip()
        if not name:
            print("[WARN] Attendance not saved: missing student name.")
            return False

        now = datetime.now()
        dt_string = now.strftime('%H:%M:%S')
        date_string = now.strftime('%Y-%m-%d')
        row = {
            'SessionID': session_id,
            'StudentID': student_id,
            'Name': name,
            'Date': date_string,
            'Time': dt_string,
        }

        file_exists = os.path.exists(file_path) and os.path.getsize(file_path) > 0
        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=ATTENDANCE_COLUMNS)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
            f.flush()
            os.fsync(f.fileno())

        print(f"Attendance saved: {name} (ID: {student_id}, session: {session_id}, {date_string} {dt_string})")
        print(f"[CSV] Saved to: {file_path}")
        return True
    except PermissionError:
        print(f"[ERROR] Cannot write to {file_path} - close Excel or any app using this file, then try again.")
        return False
    except Exception as e:
        print(f"Error marking attendance: {e}")
        return False


def write_log(message):
    try:
        os.makedirs(_project_path('logs'), exist_ok=True)
        with open(_project_path('logs', 'security_logs.txt'), 'a') as f:
            f.write(message + '\n')
    except Exception as e:
        print(f"Error writing log: {e}")


def register_new_face(frame, face_location, name):
    cv2_lib, _ = _load_libraries()
    y1, x2, y2, x1 = face_location
    padding = 20
    h, w = frame.shape[:2]
    y1 = max(0, y1 - padding)
    y2 = min(h, y2 + padding)
    x1 = max(0, x1 - padding)
    x2 = min(w, x2 + padding)
    face_img = frame[y1:y2, x1:x2]
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
    if not safe_name:
        safe_name = "person"
    filename = f"{safe_name}.jpg"
    dest_path = os.path.join(path, filename)
    counter = 1
    while os.path.exists(dest_path):
        filename = f"{safe_name}_{counter}.jpg"
        dest_path = os.path.join(path, filename)
        counter += 1
    cv2_lib.imwrite(dest_path, face_img)
    print(f"[REGISTER] Saved new face: {dest_path}")
    load_known_faces()
    return dest_path


# Background code input: stores code typed by user
_pending_code = None
_code_lock = threading.Lock()


def _read_code_thread(name, prompt_msg):
    """Thread to read code from console without blocking camera"""
    global _pending_code
    try:
        _time.sleep(0.5)
        print(f"\n{prompt_msg}", end="", flush=True)
        user_input = input().strip()
        with _code_lock:
            _pending_code = (name, user_input)
    except:
        with _code_lock:
            _pending_code = (name, "")


def _capture_code_from_camera_key(vd, key):
    """Collect numeric code input from the OpenCV camera window."""
    if key == 255:
        return None

    code_length = len(vd.get('code', ''))
    if ord('0') <= key <= ord('9'):
        vd['entered_code'] = (vd.get('entered_code', '') + chr(key))[:code_length]
        print(f"[CODE] Typed: {vd['entered_code']}")
        if len(vd['entered_code']) == code_length:
            submitted_code = vd['entered_code']
            vd['entered_code'] = ''
            return submitted_code
    elif key in (8, 127):
        vd['entered_code'] = vd.get('entered_code', '')[:-1]
    elif key == ord('c'):
        vd['entered_code'] = ''
    return None


def start_attendance():
    """
    Anti-spoofing: BLINK + required CODE shown on face.
    Attendance is marked only after both checks pass.
    Press 'Q' to exit. Press 'R' to register a face. Press 'N' for a new session.
    """
    global _pending_code, _attendance_running

    if _attendance_running:
        print("[WARN] Attendance is already running. Press Q in the camera window to stop it first.")
        from tkinter import messagebox
        messagebox.showwarning(
            "Attendance Already Running",
            "Attendance is already running.\n\nPress Q in the camera window to stop it, "
            "or press N in the camera window to start a fresh session."
        )
        return

    _attendance_running = True

    try:
        print("=" * 60)
        print("SMART ATTENDANCE SYSTEM - Anti-Spoofing Active")
        print("=" * 60)
        cv2_lib, face_rec = _load_libraries()
        
        # Pre-load dlib
        print("Loading blink detector...")
        try:
            import dlib as _dlib
            from face_recognition_models import pose_predictor_model_location
            _predictor_path = pose_predictor_model_location()
            _dlib_predictor = _dlib.shape_predictor(_predictor_path)
            print("[OK] Blink detector loaded")
        except Exception as e:
            print(f"[WARN] Could not load blink detector: {e}")
            _dlib_predictor = None
        
        print("Loading known faces...")
        load_known_faces()
        if not encodeListKnown:
            print("NOTE: No known faces loaded.")
        
        # Camera init
        print("\nOpening camera...")
        cap = None
        for attempt in range(3):
            if attempt > 0:
                _time.sleep(1.0)
            cap = cv2_lib.VideoCapture(0, cv2_lib.CAP_DSHOW)
            cap.set(cv2_lib.CAP_PROP_FRAME_WIDTH, 320)
            cap.set(cv2_lib.CAP_PROP_FRAME_HEIGHT, 240)
            if cap.isOpened():
                break
            cap.release()
            cap = cv2_lib.VideoCapture(0)
            cap.set(cv2_lib.CAP_PROP_FRAME_WIDTH, 320)
            cap.set(cv2_lib.CAP_PROP_FRAME_HEIGHT, 240)
            if cap.isOpened():
                break
        
        if cap is None or not cap.isOpened():
            print("[FAILED] Could not open camera")
            from tkinter import messagebox
            messagebox.showerror("Camera Error", "Could not open camera.")
            return
        
        print("[OK] Camera opened")

        attendance_file = prepare_attendance_file()
        if attendance_file is None:
            print("[FAILED] Cannot write attendance files. Close Excel/attendance.csv and try again.")
            from tkinter import messagebox
            messagebox.showerror(
                "Attendance File Locked",
                "Cannot save attendance.\n\nClose attendance/attendance.csv if it is open in Excel "
                "or another program, then start attendance again."
            )
            cap.release()
            cv2_lib.destroyAllWindows()
            return

        print(f"[INFO] Attendance will be saved to: {attendance_file}")
        
        # Warm up
        for warmup in range(10):
            ret, test_frame = cap.read()
            if ret and test_frame is not None and warmup == 9:
                print(f"[OK] Camera producing frames ({test_frame.shape[1]}x{test_frame.shape[0]})")
        
        print("Starting recognition loop...")
        print("[INFO] Press 'Q' to exit | 'R' to register | 'N' = new session")
        print("=" * 60)

        session_id = _next_attendance_session_id()
        _begin_attendance_session(session_id)
        print(f"[INFO] Session ID: {session_id} (one mark per student this session)")

        _last_unknown_capture = 0.0
        
        # Background thread state
        processing_lock = threading.Lock()
        latest_frame_for_processing = None
        processing_results = {'faces': [], 'encodes': [], 'ready': False, 'frame_id': 0}
        _stop_processing = False
        
        def _process_faces():
            nonlocal latest_frame_for_processing, processing_results, _stop_processing
            _, face_rec_local = _load_libraries()
            while not _stop_processing:
                with processing_lock:
                    frame_to_process = latest_frame_for_processing
                if frame_to_process is not None:
                    try:
                        imgS = cv2_lib.resize(frame_to_process, (0, 0), None, 0.5, 0.5)
                        imgS_rgb = cv2_lib.cvtColor(imgS, cv2_lib.COLOR_BGR2RGB)
                        imgS_gray = cv2_lib.cvtColor(imgS, cv2_lib.COLOR_BGR2GRAY)
                        facesCurFrame = face_rec_local.face_locations(imgS_rgb)
                        encodesCurFrame = face_rec_local.face_encodings(imgS_rgb, facesCurFrame)
                        with processing_lock:
                            processing_results['faces'] = list(zip(encodesCurFrame, facesCurFrame, [imgS_gray] * len(facesCurFrame)))
                            processing_results['encodes'] = encodesCurFrame
                            processing_results['ready'] = True
                            processing_results['frame_id'] += 1
                    except:
                        pass
                _time.sleep(0.01)
        
        processing_thread = threading.Thread(target=_process_faces, daemon=True)
        processing_thread.start()
        
        # Main display loop
        frame_count = 0
        window_name = 'Attendance - Q=exit | R=register | N=new session'
        cv2_lib.namedWindow(window_name, cv2_lib.WINDOW_NORMAL)
        print(f"[INFO] Known: {classNames}")
        print("[INFO] ANTI-SPOOF: Blink at camera, then enter the face code to mark attendance")
        
        cached_faces = []
        cached_encodes = []
        last_processed_frame_id = -1
        pending_verify = {}
        
        while True:
            frame_count += 1
            success, img = cap.read()
            if not success or img is None:
                continue
            
            with processing_lock:
                latest_frame_for_processing = img.copy()
                if processing_results['ready'] and processing_results['frame_id'] != last_processed_frame_id:
                    cached_faces = processing_results['faces']
                    cached_encodes = processing_results['encodes']
                    last_processed_frame_id = processing_results['frame_id']
            
            key = cv2_lib.waitKey(1) & 0xFF

            if key == ord('n'):
                session_id = _next_attendance_session_id()
                _begin_attendance_session(session_id)
                pending_verify.clear()
                print(f"[INFO] New session started: {session_id}")

            # Check for code input from background thread
            code_input = None
            with _code_lock:
                if _pending_code is not None:
                    code_input = _pending_code
                    _pending_code = None
            
            # Handle R key
            if key == ord('r') and len(cached_faces) > 0:
                largest_idx = 0
                largest_area = 0
                for idx, (_, faceLoc, _) in enumerate(cached_faces):
                    fy1, fx2, fy2, fx1 = faceLoc
                    area = ((fy2 - fy1) * 2) * ((fx2 - fx1) * 2)
                    if area > largest_area:
                        largest_area = area
                        largest_idx = idx
                _, best_face_loc, _ = cached_faces[largest_idx]
                fy1, fx2, fy2, fx1 = best_face_loc
                orig_loc = (fy1 * 2, fx2 * 2, fy2 * 2, fx1 * 2)
                cv2_lib.rectangle(img, (orig_loc[1], orig_loc[0]), (orig_loc[3], orig_loc[2]), (255, 0, 0), 3)
                cv2_lib.putText(img, "REGISTERING...", (orig_loc[1], orig_loc[2] + 30), cv2_lib.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                cv2_lib.imshow(window_name, img)
                cv2_lib.waitKey(500)
                print("\n[NEW FACE REGISTRATION]")
                print("Enter name: ", end="", flush=True)
                _time.sleep(0.3)
                try:
                    new_name = input().strip()
                    if new_name:
                        register_new_face(img, orig_loc, new_name)
                        print(f"[OK] Registered '{new_name}'")
                    else:
                        print("[CANCEL]")
                except:
                    pass
            
            # Draw faces
            for encodeFace, faceLoc in zip(cached_encodes, [loc for _, loc, _ in cached_faces]):
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 2, x2 * 2, y2 * 2, x1 * 2
                
                if len(encodeListKnown) == 0:
                    cv2_lib.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2_lib.putText(img, "UNKNOWN", (x1, y2 + 30), cv2_lib.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    continue
                
                try:
                    faceDis = face_rec.face_distance(encodeListKnown, encodeFace)
                    matchIndex = np.argmin(faceDis)
                    is_match = float(faceDis[matchIndex]) < 0.5
                    
                    if is_match:
                        name = classNames[matchIndex].upper()
                        # Look up student record to get ID
                        face_filename = classNames[matchIndex]
                        # Try common extensions to find the actual file
                        student_record = None
                        for ext in ['.jpg', '.jpeg', '.png']:
                            student_record = find_student_by_face(face_filename + ext)
                            if student_record:
                                break
                        if not student_record:
                            # Try with _1, _2 etc. suffixes
                            import glob
                            pattern = os.path.join('faces', face_filename + '*')
                            for fpath in glob.glob(pattern):
                                fname = os.path.basename(fpath)
                                student_record = find_student_by_face(fname)
                                if student_record:
                                    break
                        
                        student_id = student_record.get('student_id', '') if student_record else ''
                        display_name = name
                        
                        cv2_lib.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2_lib.putText(img, display_name, (x1, y2 + 30), cv2_lib.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                        
                        if not _is_marked_in_active_session(name, student_id, session_id):
                            # Start verification
                            if name not in pending_verify:
                                code = str(np.random.randint(1000, 9999))
                                pending_verify[name] = {
                                    'code': code,
                                    'blinked': False,
                                    'code_ok': False,
                                    'entered_code': '',
                                    'student_id': student_id,
                                }
                                print(f"\n[VERIFY] {name} (ID: {student_id}) - Blink, then enter code to mark attendance!")
                                print(f"[VERIFY] Code on face: {code}")
                            
                            vd = pending_verify[name]
                            camera_code = _capture_code_from_camera_key(vd, key)
                            if camera_code is not None:
                                code_input = (name, camera_code)
                            
                            # Show code on face
                            code_text = f"CODE: {vd['code']}"
                            ts = cv2_lib.getTextSize(code_text, cv2_lib.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                            tx = x1 + (x2 - x1 - ts[0]) // 2
                            ty = y1 + (y2 - y1) // 2
                            cv2_lib.rectangle(img, (tx-5, ty-ts[1]-5), (tx+ts[0]+5, ty+5), (0,0,0), -1)
                            cv2_lib.putText(img, code_text, (tx, ty), cv2_lib.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
                            
                            # Blink detection
                            if not vd['blinked'] and _dlib_predictor is not None:
                                for enc, loc, gray in cached_faces:
                                    if loc == faceLoc:
                                        fy1, fx2, fy2, fx1 = loc
                                        dlib_rect = _dlib.rectangle(left=int(fx1), top=int(fy1), right=int(fx2), bottom=int(fy2))
                                        if detect_blink(gray, dlib_rect):
                                            print(f"[VERIFY] {name} - Blink detected!")
                                            vd['blinked'] = True
                                        break
                                if not vd['blinked']:
                                    cv2_lib.putText(img, "BLINK TO VERIFY", (x1, y2+60), cv2_lib.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
                                elif not vd['code_ok']:
                                    cv2_lib.putText(img, "ENTER CODE", (x1, y2+60), cv2_lib.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

                            if name in pending_verify and not vd['code_ok']:
                                entered = vd.get('entered_code', '')
                                if entered:
                                    typed_text = f"TYPED: {entered}"
                                    cv2_lib.putText(img, typed_text, (x1, y2+90), cv2_lib.FONT_HERSHEY_SIMPLEX, 0.55, (0,255,255), 2)
                            
                            # Check if user typed the required code in the camera window.
                            if code_input is not None:
                                input_name, input_code = code_input
                                if input_name == name:
                                    if input_code == vd['code']:
                                        vd['code_ok'] = True
                                        print(f"[VERIFY] {name} - Code verified!")
                                    elif input_code:
                                        # Wrong code! Security alert
                                        print(f"[SECURITY] Wrong code for {name}: '{input_code}'")
                                        now = datetime.now().strftime('%Y%m%d_%H%M%S')
                                        spath = f'screenshots/spoof_{name}_{now}.jpg'
                                        cv2_lib.imwrite(spath, img)
                                        write_log(f"SPOOF: {name} wrong code '{input_code}'")
                                        send_malicious_alert_threaded(name, spath, input_code)
                                        # Also alert the student whose identity is being spoofed
                                        student_email = get_student_email(name)
                                        if student_email:
                                            send_student_alert_threaded(
                                                student_email,
                                                name,
                                                "Spoof Attempt",
                                                f"Someone entered a wrong verification code while attempting to mark your attendance. Screenshot saved."
                                            )
                                        cv2_lib.putText(img, "WRONG - ALERT SENT", (x1, y2+60), cv2_lib.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
                                        del pending_verify[name]
                            
                            if name in pending_verify and vd['blinked'] and vd['code_ok']:
                                if markAttendance(name, vd.get('student_id', ''), session_id):
                                    _record_session_mark(name, vd.get('student_id', ''), session_id)
                                    write_log(f"AUTHORIZED ACCESS: {name} (blink + code verified, session {session_id})")
                                    cv2_lib.putText(img, "MARKED!", (x1, y2+60), cv2_lib.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                                    del pending_verify[name]
                                else:
                                    cv2_lib.putText(img, "SAVE FAILED - CLOSE CSV", (x1, y2+60), cv2_lib.FONT_HERSHEY_SIMPLEX, 0.45, (0,0,255), 2)
                        else:
                            cv2_lib.putText(img, f"MARKED ({session_id})", (x1, y2+60), cv2_lib.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                    
                    else:
                        cv2_lib.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2_lib.putText(img, "UNKNOWN", (x1, y2+30), cv2_lib.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
                        now_ts = _time.time()
                        if now_ts - _last_unknown_capture > 5.0:
                            _last_unknown_capture = now_ts
                            now = datetime.now().strftime('%Y%m%d_%H%M%S')
                            os.makedirs('screenshots', exist_ok=True)
                            spath = f'screenshots/unknown_{now}.jpg'
                            cv2_lib.imwrite(spath, img)
                            write_log(f"UNAUTHORIZED ACCESS AT {now}")
                            send_email_alert_threaded(spath)
                
                except Exception as e:
                    print(f"[ERROR] {e}")

            cv2_lib.putText(img, f"Session: {session_id}", (10, 25), cv2_lib.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

            try:
                if cv2_lib.getWindowProperty(window_name, cv2_lib.WND_PROP_VISIBLE) < 1:
                    print("[USER] Camera window closed - stopping")
                    break
            except cv2_lib.error:
                print("[USER] Camera window closed - stopping")
                break

            cv2_lib.imshow(window_name, img)
            if key == ord('q'):
                print("[USER] Q pressed - stopping")
                break
    
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        _attendance_running = False
        _end_attendance_session()
        print("[CLEANUP] Releasing...")
        try:
            _stop_processing = True
            _time.sleep(0.1)
            if 'cap' in locals() and cap is not None:
                cap.release()
            if cv2 is not None:
                cv2.destroyAllWindows()
                cv2.waitKey(1)
            print("[OK] Done")
        except:
            pass

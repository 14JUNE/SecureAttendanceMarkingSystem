"""
Student Registration Module
Allows students to register with name, email, class, and face photo.
Photo can be captured via camera or uploaded from desktop.
Registration sends notification email to admin.
"""
import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import threading

# Lazy imports for CV2
cv2 = None
face_recognition = None

STUDENTS_DB = 'students.json'
FACES_DIR = 'faces'


def _ensure_dirs():
    os.makedirs(FACES_DIR, exist_ok=True)


def _load_libraries():
    global cv2, face_recognition
    if cv2 is None:
        import cv2 as cv2_lib
        import face_recognition as face_rec
        cv2 = cv2_lib
        face_recognition = face_rec
    return cv2, face_recognition


def load_students():
    """Load student database from JSON file"""
    if not os.path.exists(STUDENTS_DB):
        return {}
    try:
        with open(STUDENTS_DB, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_students(students):
    """Save student database to JSON file"""
    with open(STUDENTS_DB, 'w') as f:
        json.dump(students, f, indent=2)


def get_student_email(name):
    """Look up a student's email by their UPPERCASE name"""
    students = load_students()
    return students.get(name.upper(), {}).get('email', None)


def is_student_id_taken(student_id, exclude_key=None):
    """Check if a student ID is already registered. Optionally exclude a key (for updates)."""
    students = load_students()
    for key, data in students.items():
        if exclude_key and key == exclude_key:
            continue
        if data.get('student_id') == student_id:
            return key, data.get('name', 'Unknown')
    return None, None


def find_student_by_face(face_filename):
    """Look up a student's full record (including student_id) by their face file name."""
    students = load_students()
    for key, data in students.items():
        if data.get('face_file') == face_filename:
            return data
    return None


def cleanup_orphaned_students():
    """
    Remove student records from students.json if their face file no longer exists
    in the faces/ directory. This prevents orphaned records from showing up in
    attendance when face photos are manually deleted.
    """
    students = load_students()
    removed = []
    keys_to_delete = []
    
    for key, data in students.items():
        face_file = data.get('face_file', '')
        if not face_file:
            continue
        face_path = os.path.join(FACES_DIR, face_file)
        if not os.path.exists(face_path):
            keys_to_delete.append(key)
            removed.append(f"  - {data.get('name', 'Unknown')} ({key}) - face file '{face_file}' missing")
    
    if not keys_to_delete:
        return
    
    for key in keys_to_delete:
        del students[key]
    
    save_students(students)
    
    print(f"[CLEANUP] Removed {len(removed)} orphaned student record(s) with missing face files:")
    for r in removed:
        print(r)


def register_student(name, student_id, email, student_class, image_path):
    """
    Register a student: save face file + update database + notify admin.
    """
    _ensure_dirs()
    
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
    if not safe_name:
        safe_name = "person"
    
    import shutil
    filename = f"{safe_name}.jpg"
    dest_path = os.path.join(FACES_DIR, filename)
    
    counter = 1
    while os.path.exists(dest_path):
        filename = f"{safe_name}_{counter}.jpg"
        dest_path = os.path.join(FACES_DIR, filename)
        counter += 1
    
    shutil.copy2(image_path, dest_path)
    
    students = load_students()
    key = safe_name.upper()
    students[key] = {
        'name': name,
        'student_id': student_id,
        'email': email,
        'class': student_class,
        'face_file': filename,
        'registered_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_students(students)
    
    try:
        from email_alert import send_registration_notification
        threading.Thread(
            target=send_registration_notification,
            args=(students[key],),
            daemon=True
        ).start()
        print(f"[REGISTER] Email notification queued for admin")
    except Exception as e:
        print(f"[REGISTER] Could not send email: {e}")
    
    try:
        import attendence
        attendence.load_known_faces()
    except:
        pass
    
    print(f"[REGISTER] Student '{name}' registered successfully")
    return True


class RegistrationWindow:
    """Tkinter window for student registration with themed UI"""
    
    def __init__(self, parent=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Student Registration")
        self.window.geometry("550x700")
        self.window.resizable(False, False)
        self.window.configure(bg='lightblue')
        
        self.name_var = tk.StringVar()
        self.student_id_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.class_var = tk.StringVar()
        self.photo_path = None
        self.preview_label = None
        
        self._build_ui()
        
        if not parent:
            self.window.mainloop()
    
    def _build_ui(self):
        # Title
        tk.Label(self.window, text="Student Registration",
                font=("Arial", 18, "bold"), bg='lightblue').pack(pady=(15, 5))
        tk.Label(self.window, text="Fill in your details and add a face photo",
                font=("Arial", 10), fg="gray", bg='lightblue').pack(pady=(0, 10))
        
        # Form frame (white background)
        form = tk.Frame(self.window, padx=20, pady=10, bg='white', relief=tk.SUNKEN, bd=2)
        form.pack(padx=20, pady=5, fill="x")
        
        # Name
        tk.Label(form, text="Full Name *", font=("Arial", 11), bg='white').pack(anchor="w")
        tk.Entry(form, textvariable=self.name_var, font=("Arial", 11),
                width=40).pack(pady=(0, 8), fill="x")
        
        # Student ID
        tk.Label(form, text="Student ID *", font=("Arial", 11), bg='white').pack(anchor="w")
        tk.Entry(form, textvariable=self.student_id_var, font=("Arial", 11),
                width=40).pack(pady=(0, 8), fill="x")
        
        # Email
        tk.Label(form, text="Email Address *", font=("Arial", 11), bg='white').pack(anchor="w")
        tk.Entry(form, textvariable=self.email_var, font=("Arial", 11),
                width=40).pack(pady=(0, 8), fill="x")
        
        # Class
        tk.Label(form, text="Class / Course *", font=("Arial", 11), bg='white').pack(anchor="w")
        tk.Entry(form, textvariable=self.class_var, font=("Arial", 11),
                width=40).pack(pady=(0, 8), fill="x")
        
        # Separator
        ttk.Separator(form, orient="horizontal").pack(fill="x", pady=8)
        
        # Photo section
        tk.Label(form, text="Face Photo *", font=("Arial", 11, "bold"), bg='white').pack(anchor="w")
        
        # Preview area
        preview_frame = tk.Frame(form, width=200, height=180,
                                bg="#e0e0e0", relief="solid", bd=1)
        preview_frame.pack(pady=8)
        preview_frame.pack_propagate(False)
        
        self.preview_label = tk.Label(preview_frame, text="No photo selected\n\nClick one of the\nbuttons below",
                                     bg="#e0e0e0", fg="#666", font=("Arial", 10))
        self.preview_label.pack(expand=True, fill="both")
        
        # Buttons row
        btn_frame = tk.Frame(form, bg='white')
        btn_frame.pack(pady=8)
        
        tk.Button(btn_frame, text="Capture from Camera",
                 command=self._capture_from_camera,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                 padx=8, width=18).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="Upload from File",
                 command=self._upload_from_file,
                 bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
                 padx=8, width=18).pack(side="left", padx=5)
        
        # Status
        self.status_var = tk.StringVar(value="")
        tk.Label(self.window, textvariable=self.status_var,
                fg="green", font=("Arial", 10), bg='lightblue').pack(pady=5)
        
        # Register button - outside form, always visible
        tk.Button(self.window, text="REGISTER STUDENT",
                 command=self._register,
                 bg="#FF9800", fg="white", font=("Arial", 14, "bold"),
                 padx=30, pady=8, width=20).pack(pady=10)
        
        # Hint
        tk.Label(self.window, text="* Required fields - Admin will be notified by email",
                fg="gray", font=("Arial", 9), bg='lightblue').pack()
    
    def _capture_from_camera(self):
        """Open camera, show live preview, capture on click"""
        _load_libraries()
        
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        if not cap.isOpened():
            messagebox.showerror("Camera Error", "Could not open camera")
            return
        
        cv2.namedWindow("Capture Face - Press SPACE to capture, ESC to cancel")
        
        captured = False
        temp_path = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            h, w = frame.shape[:2]
            box_size = min(h, w) - 100
            x1 = (w - box_size) // 2
            y1 = (h - box_size) // 2
            cv2.rectangle(frame, (x1, y1), (x1 + box_size, y1 + box_size),
                         (0, 255, 0), 2)
            cv2.putText(frame, "Center your face, press SPACE", (50, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            cv2.imshow("Capture Face - Press SPACE to capture, ESC to cancel", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
            elif key == 32:
                temp_path = 'temp_capture.jpg'
                cv2.imwrite(temp_path, frame)
                captured = True
                break
        
        cap.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        
        if captured and temp_path:
            self.photo_path = temp_path
            self._update_preview(temp_path)
            self.status_var.set("✅ Photo captured from camera")
        else:
            self.status_var.set("")
    
    def _upload_from_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Face Photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.photo_path = file_path
            self._update_preview(file_path)
            self.status_var.set("✅ Photo uploaded from file")
    
    def _update_preview(self, image_path):
        try:
            from PIL import Image, ImageTk
            img = Image.open(image_path)
            img.thumbnail((190, 170))
            photo = ImageTk.PhotoImage(img)
            self.preview_label.config(image=photo, text="", bg="white")
            self.preview_label.image = photo
        except ImportError:
            self.preview_label.config(text=f"Photo loaded: {os.path.basename(image_path)}",
                                     bg="#d4edda", fg="#155724")
    
    def _register(self):
        name = self.name_var.get().strip()
        student_id = self.student_id_var.get().strip()
        email = self.email_var.get().strip()
        student_class = self.class_var.get().strip()
        
        errors = []
        if not name:
            errors.append("Name is required")
        if not student_id:
            errors.append("Student ID is required")
        if not email or '@' not in email:
            errors.append("Valid email is required")
        if not student_class:
            errors.append("Class is required")
        if not self.photo_path or not os.path.exists(self.photo_path):
            errors.append("Face photo is required")
        
        # Check if student ID is already taken
        if student_id:
            taken_key, taken_name = is_student_id_taken(student_id)
            if taken_key:
                errors.append(f"Student ID '{student_id}' is already registered to '{taken_name}'")
        
        if errors:
            messagebox.showerror("Validation Error",
                               "Please fix the following:\n\n" + "\n".join(errors))
            return
        
        success = register_student(name, student_id, email, student_class, self.photo_path)
        
        if success:
            messagebox.showinfo("Success",
                              f"Student '{name}' registered successfully!\n\n"
                              f"Student ID: {student_id}\n"
                              f"Face saved to faces/ folder.\n"
                              f"Admin has been notified.")
            self.window.destroy()
        else:
            messagebox.showerror("Error", "Registration failed. Check console.")


if __name__ == '__main__':
    RegistrationWindow()
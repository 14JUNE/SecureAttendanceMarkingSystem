from tkinter import *
try:
    import attendence
except ImportError:
    from SmartAttendence import attendence

root = Tk()
root.title("Smart Attendance System")
root.geometry("600x550")
root.configure(bg='lightblue')

# Title
title_label = Label(root, text="Face Recognition Attendance System", 
                    font=("Arial", 18, "bold"), bg='lightblue')
title_label.pack(pady=20)

# Information frame
info_frame = Frame(root, bg='white', relief=SUNKEN, bd=2)
info_frame.pack(pady=10, padx=20, fill=BOTH, expand=True)

info_text = """
Setup Instructions:
1. Register students using 'Register New Student' button
2. Click 'Start Attendance' to begin recognition
3. Press 'Q' to stop the camera

Features:
• Real-time face recognition
• Anti-spoofing (blink detection + verification code)
• Student registration with camera or photo upload
• Attendance logging
• Unknown person alerts via email
• Wrong code alerts to admin
"""

info_label = Label(info_frame, text=info_text, 
                   font=("Arial", 10), bg='white', justify=LEFT)
info_label.pack(padx=10, pady=10)

# Button frame
button_frame = Frame(root, bg='lightblue')
button_frame.pack(pady=10)

start_btn = Button(button_frame, text="Start Attendance", width=25, height=2,
                   command=attendence.start_attendance, bg='green', fg='white',
                   font=("Arial", 12, "bold"))
start_btn.pack(pady=5)

register_btn = Button(button_frame, text="Register New Student", width=25, height=2,
                      command=lambda: __import__('student_registration').RegistrationWindow(root),
                      bg='green', fg="white", font=("Arial", 12, "bold"))
register_btn.pack(pady=5)

# Status bar
status_label = Label(root, text="Ready", 
                    font=("Arial", 10), bg='lightyellow')
status_label.pack(pady=10, fill=X)

root.mainloop()
from tkinter import *
from tkinter import messagebox

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"


def login_system():
    def check_login():
        username = username_entry.get()
        password = password_entry.get()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            messagebox.showinfo("Login", "Login Successful!")
            root.destroy()
            try:
                import gui
            except ImportError:
                from SmartAttendence import gui
        else:
            messagebox.showerror("Error", "Invalid Credentials")
            password_entry.delete(0, END)

    root = Tk()
    root.title("Admin Login")
    root.geometry("400x350")
    root.configure(bg='lightblue')

    # Title
    title_label = Label(root, text="Smart Attendance System", 
                       font=("Arial", 20, "bold"), bg='lightblue')
    title_label.pack(pady=20)

    # Subtitle
    subtitle_label = Label(root, text="Admin Login", 
                          font=("Arial", 14), bg='lightblue')
    subtitle_label.pack(pady=5)

    # Username
    username_label = Label(root, text="Username:", font=("Arial", 11), bg='lightblue')
    username_label.pack()
    username_entry = Entry(root, width=25, font=("Arial", 11))
    username_entry.pack(pady=5)

    # Password
    password_label = Label(root, text="Password:", font=("Arial", 11), bg='lightblue')
    password_label.pack()
    password_entry = Entry(root, show="*", width=25, font=("Arial", 11))
    password_entry.pack(pady=5)

    # Login button
    login_btn = Button(root, text="Login", command=check_login, 
                      width=15, height=2, bg='green', fg='white', font=("Arial", 12, "bold"))
    login_btn.pack(pady=20)

    root.mainloop()


login_system()
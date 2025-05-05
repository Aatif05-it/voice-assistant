import tkinter as tk
from tkinter import messagebox
from firebase_setup import register_user, login_user  # Import functions

# Function to handle login
def login():
    email = email_entry.get()
    password = password_entry.get()  # Firebase checks email only
    user_id = login_user(email)
    
    if user_id:
        messagebox.showinfo("Success", f"Welcome back! User ID: {user_id}")
        root.destroy()  # Close login window after success
    else:
        messagebox.showerror("Error", "Invalid email or user not registered!")

# Function to handle registration
def register():
    email = email_entry.get()
    password = password_entry.get()
    name = name_entry.get()
    
    if name and email and password:
        result = register_user(email, password, name)
        messagebox.showinfo("Registration", result)
    else:
        messagebox.showerror("Error", "All fields are required!")

# GUI Setup
root = tk.Tk()
root.title("User Authentication")
root.geometry("350x300")

tk.Label(root, text="Name (For Registration):").pack()
name_entry = tk.Entry(root)
name_entry.pack()

tk.Label(root, text="Email:").pack()
email_entry = tk.Entry(root)
email_entry.pack()

tk.Label(root, text="Password:").pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

register_button = tk.Button(root, text="Register", command=register)
register_button.pack()

login_button = tk.Button(root, text="Login", command=login)
login_button.pack()

root.mainloop()

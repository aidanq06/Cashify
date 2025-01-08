import customtkinter as ctk
from tkinter import messagebox
import hashlib
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Database setup
client = MongoClient(MONGO_URI)
db = client['cashify']
users_col = db['users']

def hash_password(password):
    # Hash the password using SHA-256
    return hashlib.sha256(password.encode()).hexdigest()

def create_new_account_form(root, return_to_main):
    # Clear existing content in the root widget
    for widget in root.winfo_children():
        widget.destroy()

    background_frame = ctk.CTkFrame(root, bg_color='white', fg_color="white")
    background_frame.pack(fill='both', expand=True)

    entry_style = {"font": ("Real Text", 20), "width": 300, "height": 40}

    # Create form elements
    ctk.CTkLabel(background_frame, text="Register New Account", font=("Real Text", 40)).pack(pady=15)

    form_frame = ctk.CTkFrame(background_frame, bg_color='white', fg_color="white")
    form_frame.pack(pady=10)

    # First Name field
    first_name_label = ctk.CTkLabel(form_frame, text="First Name", font=("Real Text", 25))
    first_name_label.grid(row=0, column=0, padx=10, pady=10, sticky='e')
    first_name_entry = ctk.CTkEntry(form_frame, placeholder_text="John", **entry_style)
    first_name_entry.grid(row=0, column=1, padx=10, pady=10)

    # Last Name field
    last_name_label = ctk.CTkLabel(form_frame, text="Last Name", font=("Real Text", 25))
    last_name_label.grid(row=1, column=0, padx=10, pady=10, sticky='e')
    last_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Doe", **entry_style)
    last_name_entry.grid(row=1, column=1, padx=10, pady=10)

    # Email field
    email_label = ctk.CTkLabel(form_frame, text="Email", font=("Real Text", 25))
    email_label.grid(row=2, column=0, padx=10, pady=10, sticky='e')
    email_entry = ctk.CTkEntry(form_frame, placeholder_text="example@gmail.com", **entry_style)
    email_entry.grid(row=2, column=1, padx=10, pady=10)

    # Password field
    password_label = ctk.CTkLabel(form_frame, text="Password", font=("Real Text", 25))
    password_label.grid(row=3, column=0, padx=10, pady=10, sticky='e')
    password_entry = ctk.CTkEntry(form_frame, placeholder_text="********", show="*", **entry_style)
    password_entry.grid(row=3, column=1, padx=10, pady=10)

    # Status label
    status_label = ctk.CTkLabel(form_frame, text="", font=("Real Text", 18))
    status_label.grid(row=4, column=0, columnspan=2, pady=10)

    # Buttons
    submit_button = ctk.CTkButton(
        background_frame,
        text="Create Account",
        command=lambda: add_new_user(
            first_name_entry,
            last_name_entry,
            email_entry,
            password_entry,
            status_label,
            return_to_main
        ),
        font=("Real Text", 20),
        fg_color="black",
    )
    submit_button.pack(pady=20)

    back_button = ctk.CTkButton(
        background_frame,
        text="Back",
        command=return_to_main,
        font=("Real Text", 20),
        fg_color="black",
    )
    back_button.pack()

def add_new_user(first_name_entry, last_name_entry, email_entry, password_entry, status_label, return_to_main):
    first_name = first_name_entry.get()
    last_name = last_name_entry.get()
    email = email_entry.get()
    password = password_entry.get()

    if users_col.find_one({"email": email}):
        messagebox.showerror("Error", "Email already exists.")
        return

    if first_name and last_name and email and password:
        password_hash = hash_password(password)
        users_col.insert_one({
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password_hash": password_hash,
            "created_at": os.getenv('CREATED_AT'),
            "updated_at": os.getenv('UPDATED_AT'),
        })
        messagebox.showinfo("Success", "Account created!")
        return_to_main()
    else:
        messagebox.showerror("Error", "Please fill out all fields.")

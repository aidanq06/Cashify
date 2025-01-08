import customtkinter as ctk
from tkinter import messagebox
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import hashlib


class Settings:
    def __init__(self, root, return_to_dashboard, refresh_dashboard, user_id):
        self.root = root
        self.return_to_dashboard = return_to_dashboard
        self.refresh_dashboard = refresh_dashboard  # Function to refresh the dashboard
        self.user_id = user_id  # User ID for database interaction

        # Load environment variables
        load_dotenv()
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.client['cashify']
        self.users_col = self.db['users']

        # Fetch user details
        self.user_settings = self.fetch_user_details()

    def fetch_user_details(self):
        """Fetch user details from the database."""
        user = self.users_col.find_one({"_id": self.user_id})
        if user:
            return {
                "first_name": user.get("first_name", ""),
                "last_name": user.get("last_name", ""),
                "email": user.get("email", "")
            }
        else:
            messagebox.showerror("Error", "Unable to fetch user details.")
            return {"first_name": "", "last_name": "", "email": ""}

    def setup_settings_ui(self):
        # Clear previous widgets
        self.root.clear_window()

        # Background frame
        background_frame = ctk.CTkFrame(self.root, bg_color="white", fg_color="white")
        background_frame.pack(fill="both", expand=True)

        # Title
        title_label = ctk.CTkLabel(
            background_frame,
            text="Settings",
            font=("Roboto Medium", 40),
            text_color="black"
        )
        title_label.pack(pady=15)

        # Define common styles for widgets
        label_style = {"font": ("Roboto Medium", 25)}
        entry_style = {"font": ("Roboto Medium", 20), "width": 300, "height": 40}
        button_style = {"font": ("Roboto Medium", 20), "fg_color": "black", "hover_color": "#444444", "text_color": "white", "width": 200, "height": 40}

        # Profile Settings Section
        ctk.CTkLabel(background_frame, text="Profile Settings", **label_style).pack(pady=10)

        # First Name
        ctk.CTkLabel(background_frame, text="First Name:", **label_style).pack()
        first_name_entry = ctk.CTkEntry(background_frame, placeholder_text="Enter your first name", **entry_style)
        first_name_entry.insert(0, self.user_settings["first_name"])
        first_name_entry.pack(pady=10)

        # Last Name
        ctk.CTkLabel(background_frame, text="Last Name:", **label_style).pack()
        last_name_entry = ctk.CTkEntry(background_frame, placeholder_text="Enter your last name", **entry_style)
        last_name_entry.insert(0, self.user_settings["last_name"])
        last_name_entry.pack(pady=10)

        # Email
        ctk.CTkLabel(background_frame, text="Email:", **label_style).pack()
        email_entry = ctk.CTkEntry(background_frame, placeholder_text="Enter your email", **entry_style)
        email_entry.insert(0, self.user_settings["email"])
        email_entry.pack(pady=10)

        # Password Section
        ctk.CTkLabel(background_frame, text="Password (leave blank to keep current):", font=("Roboto Medium", 20)).pack()
        password_entry = ctk.CTkEntry(background_frame, placeholder_text="Enter a new password", show="*", **entry_style)
        password_entry.pack(pady=10)

        # Save Changes Button
        save_button = ctk.CTkButton(
            background_frame,
            text="Save Changes",
            command=lambda: self.save_settings(
                first_name_entry.get(),
                last_name_entry.get(),
                email_entry.get(),
                password_entry.get()
            ),
            **button_style
        )
        save_button.pack(pady=10)

        # Back Button
        back_button = ctk.CTkButton(
            background_frame,
            text="Back to Dashboard",
            command=self.refresh_dashboard,
            **button_style
        )
        back_button.pack(pady=10)

    def save_settings(self, first_name, last_name, email, password):
        """Save the updated settings to the database."""
        try:
            update_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email
            }

            # Hash and update the password if provided
            if password:
                hashed_password = self.hash_password(password)
                update_data["password_hash"] = hashed_password

            # Update the database
            self.users_col.update_one({"_id": self.user_id}, {"$set": update_data})

            messagebox.showinfo("Settings Saved", "Your settings have been saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving settings: {e}")

    @staticmethod
    def hash_password(password):
        """Hash the password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import re
import hashlib
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import random
from email.mime.text import MIMEText
import smtplib
from tkinter import messagebox

from tkextrafont import Font
from helpLogin import create_help_window
from newAccount import create_new_account_form  # Import registration functionality
from dashboard import Dashboard  # Import the dashboard functionality
from export import Export

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# Database setup
client = MongoClient(MONGO_URI)
db = client['cashify']
users_col = db['users']
transactions_col = db['transactions']
budgets_col = db['budgets']

class CashifyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window configuration
        self.custom_font = Font(file="./assets/Real Text Bold.ttf", family="Real Text")
        self.title("Cashify")
        self.geometry("1000x650")
        self.configure(bg_color='white', fg_color='white')

        # Create login screen layout
        self.setup_login_screen()

    def clear_window(self):
        # Destroy all widgets in the current window
        for widget in self.winfo_children():
            widget.destroy()

    def setup_login_screen(self):
        self.clear_window()
        self.configure(bg_color='white', fg_color='white')

        # Frames for layout
        left_frame = ctk.CTkFrame(self, width=500, height=650, bg_color='white', fg_color="white")
        left_frame.pack(side="left", fill="y", expand=False)

        right_frame = ctk.CTkFrame(self, width=500, height=650, bg_color="white", fg_color="white")
        right_frame.pack(side="right", fill="y", expand=True)

        # Add logo in the left frame
        try:
            logo_image = Image.open("./assets/mainlogo.png")
            logo_image = logo_image.resize((450, 300), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ctk.CTkLabel(left_frame, image=logo_photo, bg_color='white', text="")
            logo_label.image = logo_photo  # Keep reference to prevent garbage collection
            logo_label.pack(pady=150)
        except Exception as e:
            print(f"Error loading logo: {e}")

        # Add a thin vertical black bar
        bar_frame = ctk.CTkFrame(self, width=4, height=600, bg_color='black', fg_color="black")
        bar_frame.place(relx=0.47, rely=0.5, anchor='center')

        # Login label
        login_label = ctk.CTkLabel(right_frame, text="Login", font=("Real Text", 50), bg_color='white')
        login_label.pack(pady=30)

        # Input fields for email and password
        entry_width = 300
        entry_height = 60
        entry_font = ("Real Text", 20)

        self.email_entry = ctk.CTkEntry(right_frame, placeholder_text="Email", width=entry_width, height=entry_height, font=entry_font)
        self.email_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(right_frame, placeholder_text="Password", show="*", width=entry_width, height=entry_height, font=entry_font)
        self.password_entry.pack(pady=10)

        self.login_error_label = ctk.CTkLabel(right_frame, text="", bg_color='white', font=entry_font)
        self.login_error_label.pack(pady=(5, 20))

        # Login and Register buttons
        self.login_button = ctk.CTkButton(right_frame, text="Login", text_color="white", command=self.handle_login,
                                        width=250, height=50, font=("Real Text", 20), fg_color="#000000", hover_color="#444444")
        self.login_button.pack(pady=10)

        self.register_button = ctk.CTkButton(right_frame, text="Register", text_color="white",
                                            width=250, height=50, font=("Real Text", 20), fg_color="#000000", hover_color="#444444",
                                            command=lambda: create_new_account_form(self, self.setup_login_screen))
        self.register_button.pack(pady=10)
        """
        self.skip_button = ctk.CTkButton(
            right_frame,
            text="Skip to Dashboard",
            text_color="white",
            width=250,
            height=50,
            font=("Real Text", 20),
            fg_color="#000000",
            hover_color="#444444",
            command=self.skip_to_dashboard
        )
        self.skip_button.pack(pady=10)
        """
        # Help button configuration
        try:
            help_icon = Image.open("./assets/helpIcon.png").resize((50, 50), Image.Resampling.LANCZOS)
            help_photo = ImageTk.PhotoImage(help_icon)
            help_button = ctk.CTkButton(
                self,
                image=help_photo,
                text="",
                command=lambda: create_help_window(self, self.setup_login_screen),
                width=40,
                height=40,
                fg_color="white",
                bg_color="white",
                hover_color="#444444"
            )
            help_button.image = help_photo  # Prevent garbage collection
            help_button.place(relx=0.99, rely=0.99, anchor="se")  # Adjust placement at the bottom-right corner
        except Exception as e:
            print(f"Error loading help icon: {e}")

    def handle_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        user = users_col.find_one({"email": email})
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if user and user["password_hash"] == hashed_password:
            print("Login successful!")
            user_firstname = user.get("first_name", "User")
            

            # Fetch user budget
            budget_data = budgets_col.find_one({"user_id": user["_id"]})
            user_budget = float(budget_data["monthly_budget"]) if budget_data else 0.0

            self.show_dashboard(user["_id"])
        else:
            self.login_error_label.configure(text="Invalid Credentials", text_color="red")

    

    def validate_email(self, event=None):
        email = self.email_entry.get()
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if re.match(pattern, email):
            self.email_status_label.configure(text="Email Entered", text_color="black")
        else:
            self.email_status_label.configure(text="Incorrect Email Format", text_color="red")

    def send_verification_code(self, email):
        code = str(random.randint(100000, 999999))
        msg = MIMEText(f"Your verification code is: {code}")
        msg["Subject"] = "Your Verification Code"
        msg["From"] = SENDER_EMAIL
        msg["To"] = email

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, email, msg.as_string())
            return code
        except Exception as e:
            print(f"Error sending email: {e}")
            return None

    def verify_code(self, correct_code, entered_code):
        return correct_code == entered_code

    def handle_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        user = users_col.find_one({"email": email})
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if user and "password_hash" in user and user["password_hash"] == hashed_password:
            print("Login successful!")
            user_id = user["_id"]

            # Fetch user details (e.g., first name, budget)
            user_firstname = user.get("firstname", "User")
            user_budget = float(user.get("budget", 0.0))  # Default budget is 0.0 if not found

            # Send verification code
            self.correct_code = self.send_verification_code(email)
            if self.correct_code:
                self.show_verification_screen(email, user_firstname, user_budget, user_id)
            else:
                self.login_error_label.configure(text="Error sending verification code", text_color="red")
        else:
            self.login_error_label.configure(text="Invalid Credentials", text_color="red")


    def show_verification_screen(self, email, user_firstname, user_budget, user_id):
        self.clear_window()

        def on_verify():
            entered_code = self.code_entry.get()
            if self.verify_code(self.correct_code, entered_code):
                self.show_dashboard(user_id)
            else:
                self.verification_error_label.configure(text="Invalid Verification Code", text_color="red")

        def resend_verification_code():
            self.correct_code = self.send_verification_code(email)
            if self.correct_code:
                messagebox.showinfo("Code Resent", "A new verification code has been sent to your email.")
            else:
                messagebox.showerror("Error", "Unable to resend the verification code. Please try again later.")

        # Background frame
        background_frame = ctk.CTkFrame(self, bg_color='white', fg_color="white")
        background_frame.pack(fill='both', expand=True)
        background_frame.lower(belowThis=None)

        # Title label
        title_label = ctk.CTkLabel(
            background_frame, 
            text="Enter Verification Code", 
            font=("Roboto Medium", 50), 
            fg_color="white", 
            bg_color="white"
        )
        title_label.pack(pady=20)

        # Verification code entry
        self.code_entry = ctk.CTkEntry(
            background_frame, 
            placeholder_text="Verification Code", 
            width=500, 
            height=50, 
            font=("Roboto Medium", 25)
        )
        self.code_entry.pack(pady=(25, 0))

        # Error label for verification code
        self.verification_error_label = ctk.CTkLabel(
            background_frame, 
            text="", 
            font=("Roboto Medium", 20), 
            fg_color="white", 
            bg_color="white"
        )
        self.verification_error_label.pack(pady=(10, 0))

        # Verify button
        verify_button = ctk.CTkButton(
            background_frame, 
            text="Verify", 
            text_color="white", 
            hover_color="#444444", 
            font=("Roboto Medium", 20), 
            fg_color="black", 
            width=250, 
            height=45, 
            command=on_verify
        )
        verify_button.pack(pady=15)

        # Resend Verification Code button
        resend_button = ctk.CTkButton(
            background_frame, 
            text="Resend Verification Code", 
            text_color="white", 
            hover_color="#444444", 
            font=("Roboto Medium", 20), 
            fg_color="black", 
            width=250, 
            height=45, 
            command=resend_verification_code
        )
        resend_button.pack()

        # Logo at the bottom left
        logo_frame = ctk.CTkFrame(background_frame, bg_color='white', fg_color="white")
        logo_frame.pack(side="bottom", anchor="w", padx=20, pady=20)

        # Open the logo image
        try:
            logo_image = Image.open("./assets/cropped.png")
            original_width, original_height = logo_image.size
            new_width = int(original_width * 0.5)
            new_height = int(original_height * 0.5)
            logo_image = logo_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_image)

            # Create a label to hold the image
            logo_label = ctk.CTkLabel(logo_frame, text="", image=logo_photo, bg_color='white')
            logo_label.image = logo_photo  # Keep a reference to the image
            logo_label.pack(anchor="w")
        except Exception as e:
            print(f"Error loading logo: {e}")



    def show_dashboard(self, user_id):
        dashboard = Dashboard(self, self.setup_login_screen, user_id)
        dashboard.setup_dashboard()

    """
    def skip_to_dashboard(self):
        # Simulate a successful login with pre-defined credentials
        email = "aidanquach314@gmail.com"
        user = users_col.find_one({"email": email})
        user_id = user["_id"]

        if user:
            self.show_dashboard(user["_id"])
        else:
            self.login_error_label.configure(text="Error: User not found", text_color="red")
    """

    def navigate_to_page(self, page_name):
        print(f"Navigating to {page_name}")


if __name__ == "__main__":
    app = CashifyApp()
    app.mainloop()

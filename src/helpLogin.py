import tkinter as tk
import customtkinter as ctk
import webbrowser
from PIL import Image, ImageTk


def show_answer(frame, answer_text, return_to_main):
    for widget in frame.winfo_children():
        widget.destroy()
    ctk.CTkLabel(frame, text=answer_text, font=("Real Text", 18), wraplength=frame.winfo_width()).pack(pady=5, anchor='w')
    clear_button = ctk.CTkButton(frame, text="Clear", font=("Real Text", 18), fg_color="transparent", hover_color="#444444",
                                 text_color="black", command=lambda: clear_answer(frame, add_logo_and_back_button, return_to_main))
    clear_button.pack(pady=10)


def clear_answer(frame, callback, return_to_main):
    for widget in frame.winfo_children():
        widget.destroy()
    callback(frame, return_to_main)


def add_logo_and_back_button(frame, return_to_main):
    right = frame

    logo_image = Image.open("./assets/mainlogo.png").resize((300, 200), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = ctk.CTkLabel(right, text="", image=logo_photo, bg_color='white')
    logo_label.image = logo_photo
    logo_label.pack(pady=40)

    back_button = ctk.CTkButton(right, width=175, height=35, text="Back", command=return_to_main,
                                fg_color="black", bg_color="transparent", hover_color="#444444", text_color="white",
                                font=("Real Text", 25))
    back_button.pack(pady=10)


def create_help_window(root, return_to_main):
    for widget in root.winfo_children():
        widget.destroy()

    background_frame = ctk.CTkFrame(root, bg_color='white', fg_color="white")
    background_frame.pack(fill='both', expand=True)

    left = ctk.CTkFrame(background_frame, bg_color='white', fg_color="white")
    left.pack(side="left", fill='both', expand=True, padx=15)

    right = ctk.CTkFrame(background_frame, bg_color='white', fg_color="white")
    right.pack(side="right", fill='both', expand=True, padx=10)

    ctk.CTkLabel(left, text="Cashify Help Guide", font=("Real Text", 36)).pack(pady=5, anchor='w')

    qna_frame = ctk.CTkFrame(left, bg_color='white', fg_color="white")
    qna_frame.pack(fill='both', expand=True)

    questions_answers = [
        ("How to Login",
         "Learn how to login to your Cashify account. Follow these steps to access your account securely.\n\n"
         "Q: What credentials do I need to login?\n"
         "A: Your registered email address and password.\n\n"
         "Q: What happens if I enter incorrect credentials?\n"
         "A: You'll see an error message. Re-enter your correct email and password."),
        ("How to Register",
         "Follow these steps to create a new Cashify account.\n\n"
         "Q: What information is required?\n"
         "A: First name, last name, email, password, school, and school code."),
        ("About Cashify",
         "Cashify helps students manage their personal finances effectively.\n\n"
         "Features:\n- Budget tracking\n- Expense categorization\n- Financial goal setting.")
    ]

    for question, answer in questions_answers:
        btn = ctk.CTkButton(qna_frame, text=question, font=("Real Text", 20), fg_color="transparent",
                            hover_color="#444444", text_color="black", command=lambda a=answer: show_answer(right, a, return_to_main))
        btn.pack(fill='x', pady=5, anchor='w')

    add_logo_and_back_button(right, return_to_main)

import customtkinter as ctk
import webbrowser
from PIL import Image, ImageTk


def show_answer(frame, answer_text, return_to_main):
    for widget in frame.winfo_children():
        widget.destroy()
    ctk.CTkLabel(frame, text=answer_text, font=("Roboto Medium", 18), wraplength=frame.winfo_width()).pack(pady=5, anchor='w')
    clear_button = ctk.CTkButton(frame, text="Clear", font=("Roboto Medium", 18), fg_color="transparent",
                                 hover_color="#444444", text_color="black",
                                 command=lambda: clear_answer(frame, add_logo_and_back_button, return_to_main))
    clear_button.pack(pady=10)


def clear_answer(frame, callback, return_to_main):
    for widget in frame.winfo_children():
        widget.destroy()
    callback(frame, return_to_main)


def add_logo_and_back_button(frame, return_to_main):
    logo_image = Image.open("./assets/mainLogo.png").resize((300, 200), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = ctk.CTkLabel(frame, text="", image=logo_photo, bg_color='white')
    logo_label.image = logo_photo
    logo_label.pack(pady=40)

    hyperlink_label = ctk.CTkLabel(frame, text="Cashify GitHub Page", font=("Roboto Medium", 24), text_color="blue",
                                   fg_color="transparent", cursor="hand2")
    hyperlink_label.pack()
    hyperlink_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/aidanq06/PartnerLink"))

    back_button = ctk.CTkButton(frame, width=175, height=35, text="Back", command=return_to_main,
                                fg_color="black", bg_color="transparent", hover_color="#444444",
                                text_color="white", font=("Roboto Medium", 25))
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

    ctk.CTkLabel(left, text="Cashify Help Guide", font=("Roboto Medium", 36)).pack(pady=5, anchor='w')

    qna_frame = ctk.CTkFrame(left, bg_color='white', fg_color="white")
    qna_frame.pack(fill='both', expand=True)

    questions_answers = [
        ("Transactions", "The Transactions feature is used to add, view, update, or delete your financial transactions. "
                         "It allows you to log each expense (e.g., food, rent, or utilities) and manage your records effectively. "
                         "You can also view your transaction history in a tabular format, update incorrect entries, or delete unnecessary ones."),
        
        ("Set Budget", "The Set Budget tool allows you to define your monthly spending limit. This limit is used to compare "
                       "against your monthly spending and is reflected in the Dashboard. If you overspend, the budget indicator "
                       "will turn red. Adjust your budget as needed to reflect your financial goals."),

        ("Analyze Spending", "Analyze Spending provides insights into your financial habits using graphs. It shows your "
                             "spending trends over the last six months, comparing them to your budget. It also includes a pie chart "
                             "to display the percentage of your spending across different categories (e.g., food, rent)."),

        ("Export", "The Export feature allows you to save your transaction data in CSV or PDF formats. The CSV format is "
                   "ideal for analysis in spreadsheet software, while the PDF format is useful for printable records or sharing "
                   "with others."),

        ("Settings", "In Settings, you can update your profile information, such as your first and last name, email, and password. "
                     "All changes are saved to the database, and the updates will be reflected on the Dashboard."),

        ("Dashboard", "The Dashboard is the main hub of the application. It displays your welcome title with your first name, "
                      "your current monthly spending, and your budget. The spending indicator changes color based on your spending: "
                      "green if you're well within budget, yellow if you're approaching your limit, and red if you've overspent."),

        ("Logout", "Use the Logout button to securely end your session. All your data is automatically saved, so you won't lose "
                   "any changes. Ensure you log out on shared devices to protect your account.")
    ]

    for question, answer in questions_answers:
        btn = ctk.CTkButton(qna_frame, text=question, font=("Roboto Medium", 24), fg_color="transparent",
                            hover_color="#444444", text_color="black", anchor='w',
                            command=lambda a=answer: show_answer(right, a, return_to_main))
        btn.pack(fill='x', pady=5)

    add_logo_and_back_button(right, return_to_main)

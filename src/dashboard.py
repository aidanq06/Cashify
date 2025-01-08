import customtkinter as ctk
import datetime
from PIL import Image, ImageTk
from helpButton import create_help_window
from transactions import Transactions
from setBudget import SetBudget
from analyzeSpending import AnalyzeSpending
from export import Export
from settings import Settings
from pymongo import MongoClient
from dotenv import load_dotenv
import os


class Dashboard:
    def __init__(self, root, on_logout, user_id):
        self.root = root
        self.on_logout = on_logout
        self.user_id = user_id


        # Load environment variables
        load_dotenv()
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.client['cashify']
        self.users_col = self.db['users']
        self.budgets_col = self.db['budgets']
        self.transactions_col = self.db['transactions']

        # Fetch user details dynamically
        self.user_firstname = self.get_user_firstname()
        self.user_budget = self.get_user_budget()

        # Initialize button images
        self.button_images = [
            "./assets/transactions.png",  # Transactions
            "./assets/budget.png",  # Budget
            "./assets/analyze.png",  # Analyze Spending
            "./assets/export.png",  # Export
            "./assets/settingsButton.png",  # Settings
            "./assets/logoutButton.png"  # Logout
        ]

    def refresh_dashboard(self):
        # Fetch updated data
        self.user_budget = self.get_user_budget()
        self.user_firstname = self.get_user_firstname()
        # Re-setup the dashboard to reflect changes
        self.setup_dashboard()

    def get_user_firstname(self):
        """Fetch the user's first name from the database."""
        user = self.users_col.find_one({"_id": self.user_id})
        return user["first_name"] if user else "User"
    

    def get_user_budget(self):
        """Fetch the user's budget from the database."""
        budget_entry = self.budgets_col.find_one({"user_id": self.user_id})
        return budget_entry["monthly_budget"] if budget_entry else 0.0
    
    
    def setup_dashboard(self):
        self.root.clear_window()

        # Calculate current spending
        monthly_spending = self.calculate_monthly_spending()

        # Background frame
        background_frame = ctk.CTkFrame(self.root, bg_color='white', fg_color="white")
        background_frame.pack(fill="both", expand=True)

        # Welcome labels
        welcome_label = ctk.CTkLabel(
            background_frame,
            text=f"Welcome, {self.user_firstname}",
            font=("Roboto Medium", 50),
            text_color="black"
        )
        welcome_label.pack(pady=(10, 0), padx=15, anchor="nw")

        # Determine the color of the text based on spending
        if monthly_spending < self.user_budget * 0.75:  # Spending is far below budget
            spending_color = "green"
        else:  # Spending exceeds budget
            spending_color = "red"

        # Display budget and spending with dynamic color
        budget_label = ctk.CTkLabel(
            background_frame,
            text=f"Monthly Spending: ${monthly_spending:.2f} | Budget: ${self.user_budget:.2f}",
            font=("Roboto Medium", 25),
            text_color=spending_color
        )
        budget_label.pack(pady=(0, 15), padx=17, anchor="nw")



        # Buttons section
        buttons_frame = ctk.CTkFrame(background_frame, bg_color='white', fg_color="white")
        buttons_frame.pack(expand=True, padx=20, pady=20)

        buttonWidth = 125
        buttonHeight = 125
        buttonFont = ("Roboto Medium", 20)

        # Load button images
        button_images = [
            ImageTk.PhotoImage(Image.open(path).resize((buttonWidth, buttonHeight), Image.Resampling.LANCZOS))
            for path in self.button_images
        ]

        # Button configuration
        button_texts = [
            "Transactions", "Set Budget", "Analyze Spending",
            "Export", "Settings", "Logout"
        ]

        button_commands = [
            lambda: Transactions(self.root, self.setup_dashboard).setup_transactions(),
            lambda: SetBudget(self.root, self.setup_dashboard, self.user_id, self.refresh_dashboard).setup_set_budget_ui(),
            lambda: AnalyzeSpending(self.root, self.setup_dashboard).setup_analyze_spending_ui(),
            lambda: Export(self.root, self.setup_dashboard, self.user_id).setup_export_ui(),
            lambda: Settings(self.root, self.setup_dashboard, self.refresh_dashboard, self.user_id).setup_settings_ui(),
            self.on_logout
        ]

        # Create two rows of three buttons
        num_columns = 3
        for i in range(2):  # Two rows
            for j in range(num_columns):  # Three buttons per row
                index = i * num_columns + j
                if index < len(button_texts):
                    button = ctk.CTkButton(
                        buttons_frame,
                        text=button_texts[index],
                        image=button_images[index],
                        compound="top",
                        width=buttonWidth,
                        height=buttonHeight,
                        font=buttonFont,
                        fg_color="white",
                        bg_color="white",
                        text_color="black",
                        hover_color="#444444",
                        command=button_commands[index]
                    )
                    button.grid(row=i, column=j, padx=40, pady=20)

        # Center the columns in the grid
        for col in range(num_columns):
            buttons_frame.columnconfigure(col, weight=1)

        # Logo at bottom-left
        logo_frame = ctk.CTkFrame(background_frame, bg_color='white', fg_color="white")
        logo_frame.pack(side="bottom", anchor="w", padx=15, pady=15)

        logo_image = Image.open("./assets/cropped.png").resize((250, 70), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = ctk.CTkLabel(logo_frame, text="", image=logo_photo, bg_color='white')
        logo_label.image = logo_photo
        logo_label.pack(anchor="w")

        # Help button at bottom-right
        help_icon = Image.open("./assets/helpIcon.png").resize((50, 50), Image.Resampling.LANCZOS)
        help_photo = ImageTk.PhotoImage(help_icon)

        help_button = ctk.CTkButton(
            self.root,
            image=help_photo,
            text="",
            command=lambda: create_help_window(self.root, self.setup_dashboard),
            width=40,
            height=40,
            fg_color="white",
            bg_color="white",
            hover_color="#444444"
        )
        help_button.image = help_photo
        help_button.place(relx=1.0, rely=1.0, x=-20, y=-20, anchor="se")

    def calculate_monthly_spending(self):
        # Calculate the total spending for the current month
        current_month = datetime.datetime.now().month
        transactions = self.transactions_col.find({
            "date": {"$regex": f"^{datetime.datetime.now().year}-{current_month:02d}"}
        })
        monthly_spending = sum(float(txn["amount"]) for txn in transactions)
        return monthly_spending

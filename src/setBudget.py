import customtkinter as ctk
from pymongo import MongoClient
from dotenv import load_dotenv
import os


class SetBudget:
    def __init__(self, root, return_to_dashboard, user_id, refresh_dashboard):
        self.root = root
        self.return_to_dashboard = return_to_dashboard
        self.user_id = user_id  # Associate the budget with the logged-in user
        self.refresh_dashboard = refresh_dashboard

        # Load environment variables
        load_dotenv()
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.client['cashify']
        self.budget_col = self.db['budgets']

    def setup_set_budget_ui(self):
        # Clear previous widgets
        self.root.clear_window()

        # Background frame
        background_frame = ctk.CTkFrame(self.root, bg_color='white', fg_color='white')
        background_frame.pack(fill="both", expand=True)

        # Title
        title_label = ctk.CTkLabel(
            background_frame,
            text="Set Budget",
            font=("Roboto Medium", 50),
            text_color="black"
        )
        title_label.pack(pady=20)

        # Instruction label
        instruction_label = ctk.CTkLabel(
            background_frame,
            text="Define your budget to manage your finances effectively.",
            font=("Roboto Medium", 20),
            text_color="black"
        )
        instruction_label.pack(pady=10)

        # Display current budget
        current_budget = self.get_current_budget()
        current_budget_label = ctk.CTkLabel(
            background_frame,
            text=f"Current Monthly Budget: ${current_budget:.2f}" if current_budget is not None else "No budget set yet.",
            font=("Roboto Medium", 18),
            text_color="black"
        )
        current_budget_label.pack(pady=10)

        # Budget amount entry
        self.budget_entry = ctk.CTkEntry(
            background_frame,
            placeholder_text="Enter your monthly budget ($)",
            width=300,
            height=40,
            font=("Roboto Medium", 18)
        )
        self.budget_entry.pack(pady=20)

        # Save button
        save_button = ctk.CTkButton(
            background_frame,
            text="Save Budget",
            font=("Roboto Medium", 20),
            fg_color="black",
            hover_color="#444444",
            text_color="white",
            command=lambda: self.save_budget(current_budget_label)
        )
        save_button.pack(pady=10)

        # Back button
        back_button = ctk.CTkButton(
            background_frame,
            text="Back to Dashboard",
            font=("Roboto Medium", 20),
            fg_color="#444444",
            hover_color="black",
            text_color="white",
            command=self.refresh_dashboard
        )
        
        back_button.pack(pady=10)

        

    def get_current_budget(self):
        """Fetch the current monthly budget for the logged-in user."""
        budget_entry = self.budget_col.find_one({"user_id": self.user_id})
        return budget_entry["monthly_budget"] if budget_entry else None

    def save_budget(self, current_budget_label):
        """Validate and save the new budget for the logged-in user."""
        budget_value = self.budget_entry.get()
        try:
            # Validate input
            budget = float(budget_value)
            if budget <= 0:
                raise ValueError("Budget must be a positive number.")

            # Update the database with the user's budget
            self.budget_col.update_one(
                {"user_id": self.user_id},
                {"$set": {"monthly_budget": budget}},
                upsert=True  # Create the entry if it doesn't exist
            )

            # Update the current budget label
            current_budget_label.configure(
                text=f"Current Monthly Budget: ${budget:.2f}",
                text_color="green"
            )
            ctk.CTkLabel(
                self.root,
                text="Budget saved successfully!",
                font=("Roboto Medium", 16),
                text_color="green"
            ).pack(pady=5)

            

        except ValueError:
            error_label = ctk.CTkLabel(
                self.root,
                text="Invalid input. Please enter a valid number.",
                font=("Roboto Medium", 16),
                text_color="red"
            )
            error_label.pack(pady=5)

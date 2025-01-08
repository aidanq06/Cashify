import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

class AnalyzeSpending:
    def __init__(self, root, return_to_dashboard):
        self.root = root
        self.return_to_dashboard = return_to_dashboard

        # Load environment variables
        load_dotenv()
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.client['cashify']
        self.transactions_col = self.db['transactions']
        self.budgets_col = self.db['budgets']

    def setup_analyze_spending_ui(self):
        # Clear previous widgets
        self.root.clear_window()

        # Background frame
        background_frame = ctk.CTkFrame(self.root, bg_color='white', fg_color='white')
        background_frame.pack(fill="both", expand=True)

        # Title
        title_label = ctk.CTkLabel(
            background_frame,
            text="Analyze Spending",
            font=("Roboto Medium", 50),
            text_color="black"
        )
        title_label.pack(pady=20)

        # Instruction label
        instruction_label = ctk.CTkLabel(
            background_frame,
            text="Gain insights into your spending habits.",
            font=("Roboto Medium", 20),
            text_color="black"
        )
        instruction_label.pack(pady=10)

        # Create buttons for visualizations
        button_frame = ctk.CTkFrame(background_frame, bg_color='white', fg_color='white')
        button_frame.pack(pady=20)

        pie_chart_button = ctk.CTkButton(
            button_frame,
            text="View Category Distribution",
            font=("Roboto Medium", 20),
            fg_color="black",
            hover_color="#444444",
            text_color="white",
            command=self.show_pie_chart
        )
        pie_chart_button.pack(side="left", padx=10)

        spending_trend_button = ctk.CTkButton(
            button_frame,
            text="View Spending Charts",
            font=("Roboto Medium", 20),
            fg_color="black",
            hover_color="#444444",
            text_color="white",
            command=self.show_spending_trend
        )
        spending_trend_button.pack(side="left", padx=10)

        # Back button
        back_button = ctk.CTkButton(
            background_frame,
            text="Back to Dashboard",
            font=("Roboto Medium", 20),
            fg_color="#444444",
            hover_color="black",
            text_color="white",
            command=self.return_to_dashboard
        )
        back_button.pack(pady=20)

    def show_pie_chart(self):
        # Fetch all transactions
        transactions = self.transactions_col.find()

        # Aggregate spending by category
        data = {}
        for txn in transactions:
            category = txn["category"]
            amount = txn["amount"]
            data[category] = data.get(category, 0) + amount

        # Create a DataFrame
        df = pd.DataFrame(list(data.items()), columns=["Category", "Amount"])

        # Create a pie chart
        figure, ax = plt.subplots(figsize=(5, 5), dpi=100)
        ax.pie(df["Amount"], labels=df["Category"], autopct="%1.1f%%", startangle=140, colors=plt.cm.Paired.colors)
        ax.set_title("Spending by Category")

        # Display in Tkinter
        self.display_matplotlib_figure(figure)

    def show_spending_trend(self):
        # Get the last 6 months of data
        today = datetime.today()
        six_months_ago = today - timedelta(days=30 * 6)
        transactions = self.transactions_col.find({"date": {"$gte": six_months_ago.isoformat()}})

        # Aggregate spending by month
        spending_by_month = {}
        for txn in transactions:
            date = datetime.fromisoformat(txn["date"])
            month = date.strftime("%Y-%m")
            spending_by_month[month] = spending_by_month.get(month, 0) + txn["amount"]

        # Sort the months
        spending_by_month = dict(sorted(spending_by_month.items()))

        # Create a DataFrame
        df = pd.DataFrame(list(spending_by_month.items()), columns=["Month", "Spending"])

        # Fetch monthly budget (assuming one budget for simplicity)
        budget_entry = self.budgets_col.find_one()
        monthly_budget = budget_entry["monthly_budget"] if budget_entry else 0.0

        # Create a line chart
        figure, ax = plt.subplots(figsize=(8, 4), dpi=100)
        ax.plot(df["Month"], df["Spending"], marker="o", color="blue", label="Spending")
        ax.axhline(monthly_budget, color="red", linestyle="--", label="Monthly Budget")
        ax.set_title("Monthly Spending Trend")
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount ($)")
        ax.legend()
        ax.grid(True)

        # Rotate x-axis labels
        plt.xticks(rotation=45)

        # Display in Tkinter
        self.display_matplotlib_figure(figure)

    def display_matplotlib_figure(self, figure):
        # Clear previous widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Add Matplotlib figure to Tkinter
        canvas = FigureCanvasTkAgg(figure, master=self.root)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)

        # Add back button
        back_button = ctk.CTkButton(
            self.root,
            text="Back to Analyze Spending",
            font=("Roboto Medium", 20),
            fg_color="#444444",
            hover_color="black",
            text_color="white",
            command=self.setup_analyze_spending_ui
        )
        back_button.pack(pady=20)

import customtkinter as ctk
from tkinter import ttk, messagebox
import pandas as pd


class Manage:
    def __init__(self, root, return_to_dashboard):
        self.root = root
        self.return_to_dashboard = return_to_dashboard

    def setup_manage_ui(self):
        # Clear previous widgets
        self.root.clear_window()

        # Background frame
        background_frame = ctk.CTkFrame(self.root, bg_color='white', fg_color='white')
        background_frame.pack(fill="both", expand=True)

        # Title
        title_label = ctk.CTkLabel(
            background_frame,
            text="Manage Transactions",
            font=("Roboto Medium", 50),
            text_color="black"
        )
        title_label.pack(pady=20)

        # Instruction label
        instruction_label = ctk.CTkLabel(
            background_frame,
            text="Search, update, or delete your transactions.",
            font=("Roboto Medium", 20),
            text_color="black"
        )
        instruction_label.pack(pady=10)

        # Search Frame
        search_frame = ctk.CTkFrame(background_frame, bg_color='white', fg_color='white')
        search_frame.pack(pady=10, padx=10, fill="x")

        search_label = ctk.CTkLabel(
            search_frame,
            text="Search:",
            font=("Roboto Medium", 18),
            text_color="black"
        )
        search_label.pack(side="left", padx=(10, 5))

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by category or date")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)

        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            font=("Roboto Medium", 18),
            fg_color="black",
            hover_color="#444444",
            text_color="white",
            command=self.search_transactions
        )
        search_button.pack(side="left", padx=5)

        # Table Frame
        table_frame = ctk.CTkFrame(background_frame, bg_color='white', fg_color='white')
        table_frame.pack(pady=20, fill="both", expand=True)

        self.transactions_table = ttk.Treeview(table_frame, columns=("ID", "Date", "Category", "Amount"), show="headings")
        self.transactions_table.heading("ID", text="ID")
        self.transactions_table.heading("Date", text="Date")
        self.transactions_table.heading("Category", text="Category")
        self.transactions_table.heading("Amount", text="Amount ($)")
        self.transactions_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Sample data for testing
        self.transactions_data = pd.DataFrame([
            {"ID": 1, "Date": "2023-01-01", "Category": "Food", "Amount": 50},
            {"ID": 2, "Date": "2023-01-02", "Category": "Rent", "Amount": 1200},
            {"ID": 3, "Date": "2023-01-03", "Category": "Entertainment", "Amount": 100},
        ])
        self.update_table(self.transactions_data)

        # Action Buttons
        button_frame = ctk.CTkFrame(background_frame, bg_color='white', fg_color='white')
        button_frame.pack(pady=10)

        update_button = ctk.CTkButton(
            button_frame,
            text="Update Selected",
            font=("Roboto Medium", 18),
            fg_color="black",
            hover_color="#444444",
            text_color="white",
            command=self.update_transaction
        )
        update_button.pack(side="left", padx=10)

        delete_button = ctk.CTkButton(
            button_frame,
            text="Delete Selected",
            font=("Roboto Medium", 18),
            fg_color="red",
            hover_color="#660000",
            text_color="white",
            command=self.delete_transaction
        )
        delete_button.pack(side="left", padx=10)

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

    def update_table(self, data):
        # Clear existing table rows
        for row in self.transactions_table.get_children():
            self.transactions_table.delete(row)

        # Insert new rows
        for _, row in data.iterrows():
            self.transactions_table.insert("", "end", values=(row["ID"], row["Date"], row["Category"], row["Amount"]))

    def search_transactions(self):
        query = self.search_entry.get().strip().lower()
        if query:
            filtered_data = self.transactions_data[
                self.transactions_data["Category"].str.lower().str.contains(query) |
                self.transactions_data["Date"].str.contains(query)
            ]
            self.update_table(filtered_data)
        else:
            self.update_table(self.transactions_data)

    def update_transaction(self):
        selected_item = self.transactions_table.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a transaction to update.")
            return

        values = self.transactions_table.item(selected_item, "values")
        messagebox.showinfo("Update Transaction", f"Update transaction with ID {values[0]}.\n(Feature to be implemented.)")

    def delete_transaction(self):
        selected_item = self.transactions_table.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a transaction to delete.")
            return

        values = self.transactions_table.item(selected_item, "values")
        transaction_id = values[0]
        self.transactions_data = self.transactions_data[self.transactions_data["ID"] != int(transaction_id)]
        self.update_table(self.transactions_data)
        messagebox.showinfo("Delete Transaction", f"Transaction with ID {transaction_id} has been deleted.")

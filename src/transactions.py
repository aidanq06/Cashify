import customtkinter as ctk
from tkinter import messagebox, ttk, Toplevel
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
from tkcalendar import DateEntry
from bson import ObjectId

class Transactions:
    def __init__(self, root, return_to_dashboard):
        self.root = root
        self.return_to_dashboard = return_to_dashboard

        # Load environment variables
        load_dotenv()
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.client['cashify']
        self.transactions_col = self.db['transactions']

    def setup_transactions(self):
        # Clear the main window
        self.root.clear_window()

        # Background frame
        background_frame = ctk.CTkFrame(self.root, bg_color='white', fg_color='white')
        background_frame.pack(fill="both", expand=True)

        # Title
        title_label = ctk.CTkLabel(
            background_frame,
            text="Transactions",
            font=("Roboto Medium", 50),
            text_color="black"
        )
        title_label.pack(pady=20)

        # Instruction label
        instruction_label = ctk.CTkLabel(
            background_frame,
            text="Manage and track your financial transactions easily.",
            font=("Roboto Medium", 20),
            text_color="black"
        )
        instruction_label.pack(pady=10)

        # Main Content Area with Tab Navigation
        tab_view = ctk.CTkTabview(background_frame, width=700, height=500, fg_color="white")
        tab_view.pack(expand=True, padx=20, pady=20)

        # Add Tabs
        self.add_transaction_tab(tab_view)
        self.view_transactions_tab(tab_view)

    def add_transaction_tab(self, tab_view):
        tab = tab_view.add("Add Transaction")
        ctk.CTkLabel(tab, text="Add a New Transaction", font=("Roboto Medium", 20), bg_color='white').pack(pady=10)

        # Input Fields
        entry_style = {"font": ("Roboto Medium", 16), "width": 300, "height": 40}
        amount_entry = ctk.CTkEntry(tab, placeholder_text="Amount ($)", **entry_style)
        amount_entry.pack(pady=10)

        categories = ["Food", "Rent", "Utilities", "Entertainment", "Miscellaneous"]
        category_dropdown = ctk.CTkOptionMenu(
            tab,
            values=categories,
            font=("Roboto Medium", 16),
            width=300,
            fg_color="#f0f0f0",
            text_color="black",
            dropdown_hover_color="#d9d9d9"
        )
        category_dropdown.pack(pady=10)

        description_entry = ctk.CTkEntry(tab, placeholder_text="Description (Optional)", **entry_style)
        description_entry.pack(pady=10)

        date_picker = DateEntry(tab, font=("Roboto Medium", 16), date_pattern="yyyy-mm-dd", width=30, background="gray")
        date_picker.pack(pady=10)

        # Save Button
        save_button = ctk.CTkButton(
            tab,
            text="Save Transaction",
            font=("Roboto Medium", 20),
            fg_color="#000000",
            hover_color="#444444",
            text_color="white",
            width=300,
            height=50,
            command=lambda: self.add_transaction(
                amount_entry.get(),
                category_dropdown.get(),
                description_entry.get(),
                date_picker.get_date()
            )
        )
        save_button.pack(pady=10)

        # Back to Dashboard Button
        back_button = ctk.CTkButton(
            tab,
            text="Back to Dashboard",
            font=("Roboto Medium", 20),
            fg_color="#444444",
            hover_color="black",
            text_color="white",
            width=300,
            height=50,
            command=self.return_to_dashboard
        )
        back_button.pack(pady=10)

    def add_transaction(self, amount, category, description, date):
        try:
            amount = float(amount)
            transaction = {
                "amount": amount,
                "category": category,
                "description": description,
                "date": date.isoformat(),  # Save date as ISO string
            }
            self.transactions_col.insert_one(transaction)
            messagebox.showinfo("Success", "Transaction added successfully!")
            self.return_to_dashboard()  # Automatically return to dashboard
        except ValueError:
            messagebox.showerror("Error", "Invalid amount. Please try again.")

    def view_transactions_tab(self, tab_view):
        tab = tab_view.add("View Transactions")
        ctk.CTkLabel(tab, text="View and Manage Transactions", font=("Roboto Medium", 20), bg_color='white').pack(pady=10)

        # Table Frame
        table_frame = ctk.CTkFrame(tab, fg_color="white")
        table_frame.pack(fill="both", expand=True, padx=0, pady=10)

        self.transactions_table = ttk.Treeview(
            table_frame,
            columns=("ID", "Date", "Category", "Amount", "Description"),
            show="headings"
        )
        self.transactions_table.heading("ID", text="ID")
        self.transactions_table.heading("Date", text="Date")
        self.transactions_table.heading("Category", text="Category")
        self.transactions_table.heading("Amount", text="Amount ($)")
        self.transactions_table.heading("Description", text="Description")
        self.transactions_table.pack(fill="both", expand=True)

        # Fetch and Populate Data
        self.refresh_transactions()

        # Action Buttons
        button_frame = ctk.CTkFrame(tab, bg_color='white', fg_color='white')
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

    def refresh_transactions(self):
        # Clear existing table rows
        for row in self.transactions_table.get_children():
            self.transactions_table.delete(row)

        # Fetch transactions from the database
        transactions = self.transactions_col.find().sort("date", -1)
        for txn in transactions:
            self.transactions_table.insert(
                "",
                "end",
                values=(
                    str(txn["_id"]),
                    txn["date"],
                    txn["category"],
                    f"${txn['amount']:.2f}",
                    txn.get("description", "")
                )
            )

    def update_transaction(self):
        selected_item = self.transactions_table.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a transaction to update.")
            return

        values = self.transactions_table.item(selected_item, "values")
        transaction_id = values[0]

        # Create Update Modal
        modal = Toplevel(self.root)
        modal.title("Update Transaction")
        modal.geometry("400x400")

        # Input Fields in Modal
        entry_style = {"font": ("Roboto Medium", 14), "width": 200}
        amount_entry = ctk.CTkEntry(modal, placeholder_text="Amount ($)", **entry_style)
        amount_entry.insert(0, values[3].strip("$"))
        amount_entry.pack(pady=10)

        category_entry = ctk.CTkEntry(modal, placeholder_text="Category", **entry_style)
        category_entry.insert(0, values[2])
        category_entry.pack(pady=10)

        description_entry = ctk.CTkEntry(modal, placeholder_text="Description", **entry_style)
        description_entry.insert(0, values[4])
        description_entry.pack(pady=10)

        date_entry = DateEntry(modal, font=("Roboto Medium", 14), date_pattern="yyyy-mm-dd")
        date_entry.set_date(values[1])
        date_entry.pack(pady=10)

        def save_updates():
            try:
                # Convert transaction_id to ObjectId
                transaction_object_id = ObjectId(transaction_id)

                updated_transaction = {
                    "amount": float(amount_entry.get()),
                    "category": category_entry.get(),
                    "description": description_entry.get(),
                    "date": date_entry.get_date().isoformat(),
                }
                self.transactions_col.update_one(
                    {"_id": transaction_object_id}, {"$set": updated_transaction}
                )
                messagebox.showinfo("Success", "Transaction updated successfully!")
                self.refresh_transactions()
                modal.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid data. Please try again.")
            except Exception as e:
                print(f"Error updating transaction: {e}")
                messagebox.showerror("Error", "An error occurred while updating the transaction.")

        save_button = ctk.CTkButton(
            modal,
            text="Save Updates",
            font=("Roboto Medium", 16),
            fg_color="#000000",
            hover_color="#444444",
            text_color="white",
            command=save_updates
        )
        save_button.pack(pady=10)


    def delete_transaction(self):
        selected_items = self.transactions_table.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select one or more transactions to delete.")
            return

        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected transactions?")
        if not confirm:
            return

        # Collect transaction IDs from the selected rows
        transaction_ids = [self.transactions_table.item(item, "values")[0] for item in selected_items]

        # Perform deletion in the database
        for transaction_id in transaction_ids:
            try:
                # Convert transaction_id to ObjectId
                self.transactions_col.delete_one({"_id": ObjectId(transaction_id)})
            except Exception as e:
                print(f"Error deleting transaction with ID {transaction_id}: {e}")
                messagebox.showerror("Error", f"Failed to delete transaction with ID {transaction_id}")

        # Refresh the transactions table
        self.refresh_transactions()

        # Show success message
        messagebox.showinfo(
            "Delete Transactions",
            f"{len(transaction_ids)} transaction(s) have been deleted successfully."
        )
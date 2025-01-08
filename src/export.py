import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
from fpdf import FPDF
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import ObjectId

class Export:
    def __init__(self, root, return_to_dashboard, user_id):
        self.root = root
        self.return_to_dashboard = return_to_dashboard
        self.user_id = user_id

        # Load environment variables
        load_dotenv()
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.client['cashify']
        self.transactions_col = self.db['transactions']

    def setup_export_ui(self):
        # Clear previous widgets
        self.root.clear_window()

        # Background frame
        background_frame = ctk.CTkFrame(self.root, bg_color="white", fg_color="white")
        background_frame.pack(fill="both", expand=True)

        # Title
        title_label = ctk.CTkLabel(
            background_frame,
            text="Export Transactions",
            font=("Roboto Medium", 50),
            text_color="black"
        )
        title_label.pack(pady=20)

        # Instruction label
        instruction_label = ctk.CTkLabel(
            background_frame,
            text="Export your transaction data to CSV or PDF format.",
            font=("Roboto Medium", 20),
            text_color="black"
        )
        instruction_label.pack(pady=10)

        # Export Buttons
        button_frame = ctk.CTkFrame(background_frame, bg_color="white", fg_color="white")
        button_frame.pack(pady=30)

        export_csv_button = ctk.CTkButton(
            button_frame,
            text="Export to CSV",
            font=("Roboto Medium", 20),
            fg_color="black",
            hover_color="#444444",
            text_color="white",
            command=self.export_to_csv
        )
        export_csv_button.pack(side="left", padx=20)

        export_pdf_button = ctk.CTkButton(
            button_frame,
            text="Export to PDF",
            font=("Roboto Medium", 20),
            fg_color="black",
            hover_color="#444444",
            text_color="white",
            command=self.export_to_pdf
        )
        export_pdf_button.pack(side="left", padx=20)

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

    def fetch_transactions(self):
        """Fetch transaction data for the current user."""
        transactions = self.transactions_col.find({"user_id": str(self.user_id)})  # Ensure user_id is a string
        data = []
        for txn in transactions:
            data.append({
                "Date": txn["date"],
                "Category": txn["category"],
                "Amount": txn["amount"],
                "Description": txn.get("description", "")
            })
        return pd.DataFrame(data)

    def export_to_csv(self):
        try:
            # Fetch transaction data
            transactions_data = self.fetch_transactions()

            if transactions_data.empty:
                messagebox.showwarning("No Data", "No transactions available to export.")
                return

            # Open file dialog to select save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Save CSV"
            )
            if file_path:
                transactions_data.to_csv(file_path, index=False)
                messagebox.showinfo("Export Successful", f"Transactions exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred: {e}")

    def export_to_pdf(self):
        try:
            # Fetch transaction data
            transactions_data = self.fetch_transactions()

            if transactions_data.empty:
                messagebox.showwarning("No Data", "No transactions available to export.")
                return

            # Open file dialog to select save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save PDF"
            )
            if file_path:
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                pdf.set_font("Arial", size=12)

                # Add Title
                pdf.set_font("Arial", style="B", size=16)
                pdf.cell(200, 10, txt="Transaction Data", ln=True, align="C")
                pdf.ln(10)

                # Add Table Header
                pdf.set_font("Arial", style="B", size=12)
                headers = transactions_data.columns
                for header in headers:
                    pdf.cell(50, 10, txt=header, border=1, align="C")
                pdf.ln()

                # Add Table Data
                pdf.set_font("Arial", size=12)
                for _, row in transactions_data.iterrows():
                    for item in row:
                        pdf.cell(50, 10, txt=str(item), border=1, align="C")
                    pdf.ln()

                pdf.output(file_path)
                messagebox.showinfo("Export Successful", f"Transactions exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred: {e}")

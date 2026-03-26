from datetime import datetime
from .money_db import MoneyServiceDB

class Finny:
    def __init__(self):
        self.db = MoneyServiceDB()

    def add_transaction(self, user_id):
        print("\n" + "="*50)
        print("  FINNY - ADD TRANSACTION")
        print("="*50)
        
        try:
            amount = float(input("Amount:  ").strip())
            if amount <= 0:
                print("  Amount must be positive")
                return False
        except ValueError:
            print("  Invalid amount")
            return False

        category = input("Category (Food, Transport, Shopping, Entertainment, etc.): ").strip()
        if not category:
            print("  Category is required")
            return False
            
        merchant = input("Merchant/Store: ").strip()
        if not merchant:
            print("  Merchant is required")
            return False

        date_input = input("Date (YYYY-MM-DD) or press Enter for today: ").strip()
        if not date_input:
            date = datetime.now().strftime("%Y-%m-%d")
        else:
            try:
                datetime.strptime(date_input, "%Y-%m-%d")
                date = date_input
            except ValueError:
                print("  Invalid date format. Use YYYY-MM-DD")
                return False

        description = input("Description (optional): ").strip()

        # Save transaction
        transaction_id = self.db.add_transaction(user_id, amount, category, merchant, date, description)
        
        print(f"  Transaction added successfully!")
        print(f"  Transaction ID: {transaction_id}")
        print(f"  Amount:  {amount}")
        print(f"  Category: {category}")
        print(f"  Merchant: {merchant}")
        print(f"  Date: {date}")
        
        return True

    def view_transactions(self, user_id):
        print("\n" + "="*50)
        print("  FINNY - MY TRANSACTIONS")
        print("="*50)
        
        transactions = self.db.get_transactions(user_id)
        
        if not transactions:
            print("  No transactions found")
            return

        print(f"\nTotal Transactions: {len(transactions)}\n")
        
        for idx, trans in enumerate(transactions, 1):
            print(f"[{idx}]  {trans[2]:.2f} - {trans[3]}")
            print(f"      {trans[4]}")
            print(f"      {trans[5]}")
            if trans[6]:
                print(f"      {trans[6]}")
            print("-" * 40)

    def get_monthly_summary(self, user_id):
        print("\n" + "="*50)
        print("  FINNY - MONTHLY SUMMARY")
        print("="*50)
        
        try:
            month = int(input("Month (1-12): ").strip())
            year = int(input("Year: ").strip())
        except ValueError:
            print("  Invalid input")
            return

        summary = self.db.get_monthly_summary(user_id, month, year)
        
        if not summary:
            print(f"  No transactions found for {month:02d}/{year}")
            return

        month_name = datetime(year, month, 1).strftime("%B")
        print(f"\n  Spending Summary - {month_name} {year}")
        print("=" * 50)
        
        total_spending = 0
        for category, amount, count in summary:
            print(f"  {category}:  {amount:.2f} ({count} transactions)")
            total_spending += amount
        
        print("=" * 50)
        print(f"  Total Spending:  {total_spending:.2f}")
        
        # Simple pie chart representation
        print("\n  Spending Breakdown:")
        for category, amount, count in summary:
            percentage = (amount / total_spending) * 100 if total_spending > 0 else 0
            bar_length = int(percentage / 2)  # Scale down for display
            bar = " " * bar_length
            print(f"{category:12} {bar} {percentage:.1f}%")

    def show_menu(self, user_id):
        while True:
            print("\n" + "="*50)
            print("  FINNY - FINANCIAL ASSISTANT")
            print("="*50)
            print("1.   Add Transaction")
            print("2.   View Transactions")
            print("3.   Monthly Summary")
            print("4.    Back to Money Service")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self.add_transaction(user_id)
            elif choice == "2":
                self.view_transactions(user_id)
            elif choice == "3":
                self.get_monthly_summary(user_id)
            elif choice == "4":
                return
            else:
                print("  Invalid choice")
            
            input("\nPress Enter to continue...")

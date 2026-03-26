import re
from datetime import datetime
from .advanced_finny_db import AdvancedFinnyDB
from .advanced_analytics import AdvancedAnalytics

class NaturalLanguageFinny:
    def __init__(self):
        self.db = AdvancedFinnyDB()
        self.analytics = AdvancedAnalytics()
        
        # Category keywords mapping
        self.category_keywords = {
            'food': ['food', 'breakfast', 'lunch', 'dinner', 'snacks', 'coffee', 'groceries', 'meal', 'eating', 'restaurant', 'cafe', 'dosa', 'pizza', 'burger'],
            'entertainment': ['entertainment', 'movie', 'movies', 'game', 'games', 'subscription', 'netflix', 'prime', 'concert', 'streaming', 'fun'],
            'transport': ['transport', 'fuel', 'petrol', 'diesel', 'auto', 'cab', 'taxi', 'uber', 'ola', 'bus', 'train', 'metro', 'parking', 'travel'],
            'shopping': ['shopping', 'shop', 'clothes', 'clothing', 'electronics', 'phone', 'laptop', 'grocery', 'groceries', 'amazon', 'flipkart', 'store'],
            'other': ['bill', 'bills', 'healthcare', 'medical', 'medicine', 'education', 'fees', 'course', 'personal', 'care', 'miscellaneous', 'misc', 'other']
        }
        
        # Common merchant names
        self.common_merchants = {
            'food': ['restaurant', 'cafe', 'dosa', 'pizza', 'burger', 'subway', 'mcdonald', 'kfc', 'domino', 'starbucks', 'cafe coffee day'],
            'transport': ['uber', 'ola', 'cab', 'taxi', 'metro', 'bus', 'auto', 'rickshaw'],
            'shopping': ['amazon', 'flipkart', 'myntra', 'ajio', 'store', 'mall', 'shop'],
            'entertainment': ['netflix', 'prime', 'hotstar', 'spotify', 'pvr', 'inox', 'cinema']
        }

    def natural_language_entry(self, user_id):
        print("\n" + "="*60)
        print("  NATURAL LANGUAGE FINNY - CHAT STYLE")
        print("="*60)
        print("  Just tell me how you spent money today!")
        print("  Examples:")
        print("     food 200 entertainment 300 transport 150")
        print("     lunch 150 at subway movie 200 at pvr")
        print("     spent 500 on shopping 200 on food")
        print("     breakfast 100 lunch 150 dinner 200")
        print("\n  Type your expenses (or 'help' for examples):")
        
        while True:
            user_input = input("\n  You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'back']:
                break
            elif user_input.lower() == 'help':
                self._show_help()
                continue
            elif user_input.lower() == 'today':
                self._show_today_summary(user_id)
                continue
            elif not user_input:
                print("  Tell me about your expenses...")
                continue
            
            # Parse the natural language input
            transactions = self._parse_natural_language(user_input)
            
            if transactions:
                # Save transactions with intelligent features
                saved_transactions = []
                for trans in transactions:
                    # Get suggested category for merchant
                    suggested_category = self.analytics.get_suggested_category(trans['merchant'])
                    if suggested_category and suggested_category != trans['category']:
                        print(f"  Suggestion: '{trans['merchant']}' is usually categorized as '{suggested_category}'")
                        use_suggested = input("Use suggested category? (yes/no): ").strip().lower()
                        if use_suggested in ['yes', 'y']:
                            trans['category'] = suggested_category
                    
                    # Check for duplicates
                    is_duplicate = self.analytics.check_duplicate_transaction(
                        user_id, trans['amount'], trans['category'], 
                        trans['merchant'], trans['date']
                    )
                    
                    if is_duplicate:
                        print(f"\n   Possible duplicate transaction detected!")
                        print(f"  Amount:  {trans['amount']}")
                        print(f"  Category: {trans['category']}")
                        print(f"  Merchant: {trans['merchant']}")
                        print(f"  Date: {trans['date']}")
                        
                        confirm = input("Confirm save? (yes/no): ").strip().lower()
                        if confirm not in ['yes', 'y']:
                            print("  Transaction cancelled")
                            continue
                    
                    # Learn merchant-category mapping
                    self.analytics.learn_merchant_category(trans['merchant'], trans['category'])
                    
                    # Save transaction
                    transaction_id = self.db.add_transaction(
                        user_id, trans['amount'], trans['category'], 
                        trans['merchant'], trans['date'], trans['description']
                    )
                    
                    if transaction_id:
                        trans['id'] = transaction_id
                        saved_transactions.append(trans)
                        print(f"  Transaction saved successfully! ID: {transaction_id}")
                    else:
                        print(f"  Failed to save transaction")
                
                # Show summary
                self._show_parsed_summary(saved_transactions)
                
                # Ask if more expenses
                more = input("\n  Any more expenses? (type 'yes' or just continue): ").strip()
                if more.lower() not in ['yes', 'y', '']:
                    break
            else:
                print("  I couldn't understand that. Try examples like:")
                print("     food 200 entertainment 300")
                print("     lunch 150 dinner 200")

    def _parse_natural_language(self, text):
        """Parse natural language expense input"""
        transactions = []
        text = text.lower()
        
        # Pattern 3: "category amount at merchant" (most specific)
        # lunch 150 at subway movie 200 at pvr
        pattern3 = r'([a-zA-Z]+)\s+(\d+(?:\.\d+)?)\s+at\s+([a-zA-Z\s]+?)(?=\s+[a-zA-Z]+\s+\d+|$)'
        matches3 = re.findall(pattern3, text)
        
        if matches3:
            for category, amount, merchant in matches3:
                category = self._normalize_category(category)
                if category and float(amount) > 0:
                    transactions.append({
                        'amount': float(amount),
                        'category': category,
                        'merchant': merchant.strip().title(),
                        'date': datetime.now().strftime("%Y-%m-%d"),
                        'description': f"{category.title()} at {merchant.strip().title()}"
                    })
            return transactions  # Return early if we found specific pattern
        
        # Pattern 2: "amount on/at category" (natural language)
        # spent 200 on food 300 on entertainment
        pattern2 = r'(\d+(?:\.\d+)?)\s+(?:on|at)\s+([a-zA-Z]+)'
        matches2 = re.findall(pattern2, text)
        
        if matches2:
            for amount, category in matches2:
                category = self._normalize_category(category)
                if category and float(amount) > 0:
                    merchant = self._extract_merchant(text, category)
                    transactions.append({
                        'amount': float(amount),
                        'category': category,
                        'merchant': merchant,
                        'date': datetime.now().strftime("%Y-%m-%d"),
                        'description': f"{category.title()} expense"
                    })
            return transactions  # Return early if we found natural language pattern
        
        # Pattern 1: "category amount" pairs (simple format)
        # food 200 entertainment 300 transport 150
        pattern1 = r'([a-zA-Z]+)\s*(\d+(?:\.\d+)?)'
        matches1 = re.findall(pattern1, text)
        
        if matches1:
            for category, amount in matches1:
                category = self._normalize_category(category)
                if category and float(amount) > 0:
                    merchant = self._extract_merchant(text, category)
                    transactions.append({
                        'amount': float(amount),
                        'category': category,
                        'merchant': merchant,
                        'date': datetime.now().strftime("%Y-%m-%d"),
                        'description': f"{category.title()} expense"
                    })
        
        return transactions

    def _normalize_category(self, category):
        """Normalize category name to standard categories"""
        category = category.lower().strip()
        
        # Direct match
        if category in self.category_keywords:
            return category
        
        # Keyword matching
        for std_category, keywords in self.category_keywords.items():
            if category in keywords:
                return std_category
        
        # Partial matching
        for std_category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in category or category in keyword:
                    return std_category
        
        return 'other'

    def _extract_merchant(self, text, category):
        """Extract merchant name from text"""
        text_lower = text.lower()
        
        # Check for common merchants
        if category in self.common_merchants:
            for merchant in self.common_merchants[category]:
                if merchant in text_lower:
                    return merchant.title()
        
        # Look for "at merchant" pattern
        at_pattern = rf'{category}\s+\d+(?:\.\d+)?\s+at\s+([a-zA-Z\s]+?)(?=\s+[a-zA-Z]+\s+\d+|$)'
        at_match = re.search(at_pattern, text_lower)
        if at_match:
            return at_match.group(1).strip().title()
        
        # Default merchant
        return f"{category.title()} Store"

    def _show_parsed_summary(self, transactions):
        """Show summary of parsed transactions"""
        print("\n" + "="*50)
        print("  EXPENSES RECORDED")
        print("="*50)
        
        total = 0
        for trans in transactions:
            print(f"   {trans['amount']:.2f} - {trans['category'].title()}")
            print(f"     {trans['merchant']}")
            total += trans['amount']
        
        print(f"\n  Total:  {total:.2f}")
        print(f"  {len(transactions)} transactions saved!")

    def _show_help(self):
        """Show help examples"""
        print("\n" + "="*50)
        print("  HOW TO TELL ME ABOUT EXPENSES")
        print("="*50)
        
        print("\n  SIMPLE FORMAT:")
        print("   food 200 entertainment 300 transport 150")
        print("   breakfast 100 lunch 150 dinner 200")
        print("   shopping 500 bills 200 education 300")
        
        print("\n  WITH MERCHANTS:")
        print("   lunch 150 at subway dinner 200 at restaurant")
        print("   movie 200 at pvr coffee 100 at starbucks")
        print("   transport 300 at ola shopping 2000 at amazon")
        
        print("\n  NATURAL LANGUAGE:")
        print("   spent 200 on food 300 on entertainment")
        print("   paid 150 for lunch 200 for shopping")
        print("   bought groceries for 500 fuel for 1000")
        
        print("\n  QUICK COMMANDS:")
        print("   help - Show this help")
        print("   today - Show today's summary")
        print("   exit/quit - Go back")
        
        print("\n  CATEGORIES I UNDERSTAND:")
        print("   Food: food, breakfast, lunch, dinner, snacks, coffee, groceries")
        print("   Entertainment: movie, games, subscription, streaming")
        print("   Transport: fuel, auto, cab, uber, ola, bus, train")
        print("   Shopping: clothes, electronics, amazon, flipkart, store")
        print("   Other: bills, healthcare, education, miscellaneous")

    def _show_today_summary(self, user_id):
        """Show today's spending summary"""
        today = datetime.now().strftime("%Y-%m-%d")
        transactions = self.db.get_transactions(user_id)
        
        today_transactions = [t for t in transactions if t[5] == today]
        
        if not today_transactions:
            print(f"\n  No expenses recorded for today ({today})")
            return
        
        print(f"\n  TODAY'S SUMMARY ({today})")
        print("="*40)
        
        total = 0
        category_totals = {}
        
        for trans in today_transactions:
            amount = trans[2]
            category = trans[3]
            merchant = trans[4]
            
            total += amount
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += amount
            
            print(f"   {amount:.2f} - {category.title()} at {merchant}")
        
        print(f"\n  Total Today:  {total:.2f}")
        print(f"  Categories:")
        for category, amount in category_totals.items():
            percentage = (amount / total) * 100 if total > 0 else 0
            print(f"   {category.title()}:  {amount:.2f} ({percentage:.1f}%)")

    def show_menu(self, user_id):
        while True:
            print("\n" + "="*60)
            print("  NATURAL LANGUAGE FINNY - CHAT STYLE")
            print("="*60)
            print("1.   Chat Entry (Natural Language)")
            print("2.   View Transactions")
            print("3.   Today's Summary")
            print("4.   Help & Examples")
            print("5.   Advanced Analytics Dashboard")
            print("6.    Back to Money Service")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self.natural_language_entry(user_id)
            elif choice == "2":
                self._view_transactions(user_id)
            elif choice == "3":
                self._show_today_summary(user_id)
            elif choice == "4":
                self._show_help()
            elif choice == "5":
                from .intelligent_finny import IntelligentFinny
                intelligent_finny = IntelligentFinny()
                intelligent_finny.show_comprehensive_dashboard(user_id)
            elif choice == "6":
                return
            else:
                print("  Invalid choice")

    def _view_transactions(self, user_id):
        """View transactions with enhanced formatting"""
        print("\n" + "="*50)
        print("  MY TRANSACTIONS")
        print("="*50)
        
        transactions = self.db.get_transactions(user_id)
        
        if not transactions:
            print("  No transactions found")
            print("  Start by telling me about your expenses!")
            return

        print(f"\nTotal Transactions: {len(transactions)}\n")
        
        for idx, trans in enumerate(transactions, 1):
            print(f"[{idx}]  {trans[2]:.2f} - {trans[4]}")
            print(f"      {trans[3].title()}")
            print(f"      {trans[5]}")
            if trans[6]:
                print(f"      {trans[6]}")
            print("-" * 40)

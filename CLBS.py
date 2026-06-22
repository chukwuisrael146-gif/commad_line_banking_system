import json
import random
import hashlib
import os
from getpass import getpass
from datetime import datetime


class BankingSystem:

    def __init__(self, data_file="bank_data.json"):
        self.data_file = data_file
        self.accounts = {}
        self.load_data()

    # =========================
    # DATA PERSISTENCE
    # =========================
    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.accounts, f, indent=4)

    def load_data(self):
        try:
            with open(self.data_file, "r") as f:
                self.accounts = json.load(f)
        except FileNotFoundError:
            self.accounts = {}
            
    # ============
    # BCRYPT PIN HASHING
    # ============
    def hash_pin(self, pin):
        salt = os.urandom(16)

        key = hashlib.pbkdf2_hmac(
            'sha256',
            pin.encode(),
            salt,
            100000
        )
        
        return (salt + key).hex()
    


    def verify_pin(self, pin, stored_hash):
        
        data = bytes.fromhex(stored_hash)

        salt = data[:16]
        original_key = data[16:]

        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            pin.encode(),
            salt,
            100000
        )
        
        return new_key == original_key
    
    def invalid_attempts(self, attempts):
        
        attempts += 1
        
        remaining = 3 - attempts
        
        if remaining > 0:
            print(f"Invalid input. {remaining} attempts remaining.")

        else:
            print("Too many invalid attempts.")
            print("System terminated.")
            exit()

        return attempts
    

    # =========================
    # ACCOUNT NUMBER
    # =========================
    def generate_account_number(self):
        while True:
            acc = str(random.randint(100000000, 999999999))
            if acc not in self.accounts:
                return acc

    # =========================
    # PIN VALIDATION (4 DIGITS)
    # =========================
    def is_valid_pin(self, pin):
        return pin.isdigit() and len(pin) == 4

    # =========================
    # ADMIN LOGIN
    # =========================
    def admin_login(self):
        
        attempts = 0
        
        while attempts < 3:
        
            username = input("Admin username: ")
            password = getpass("Admin password: ")

            
            if username == "admin" and password == "admin123":
                return True
            
            attempts += 1
            
            remaining = 3 - attempts
            
            if remaining:
                print(
                    f"Wrong credentials."
                    f"{remaining} attempts remaining."
                )
        
        print("Too many attempts.")
        exit()

    # =========================
    # AUTHENTICATION (PIN + LOCK SYSTEM)
    # =========================
    def authenticate(self):
        
        acc = input("Enter Account Number: ").strip()

        if acc not in self.accounts:
            print("Account not found.")
            return None
        
        if self.accounts[acc].get("locked", False):
            print("Account is locked.")
            return None
        
        attempts = 0
        
        while attempts < 3:
            
            pin = input("Enter PIN: ").strip()


            stored_hash = self.accounts[acc]["pin"]

            if self.verify_pin(pin, stored_hash):
                return acc
            
            attempts += 1
            remaining = 3 - attempts
            
            if remaining > 0:
                print(f"Wrong PIN. {remaining} attempts remaning.")

            else:
                print("Account Locked")

                self.accounts[acc]["locked"] = True
                self.save_data()

                return None
            
    def user_menu(self, account):

        attempts = 0
        
        while True:


            print("\n===================")
            print(
                f"Welcome "
                f"{self.accounts[account]['name']}"
            )

            print("===================")


            print("1. Deposit")
            print("2. Withdraw")
            print("3. Transfer")
            print("4. Balance")
            print("5. Transactions")
            print("6. Logout")


            choice = input("Select: ").lower()



            if choice in ["1","deposit"]:
                attempts = 0
                self.deposit(account)



            elif choice in ["2","withdraw"]:
                attempts = 0
                self.withdraw(account)



            elif choice in ["3","transfer"]:
                attempts = 0
                self.transfer(account)


    
            elif choice in ["4","balance"]:
                attempts = 0
                self.view_balance(account)



            elif choice in ["5","transactions"]:
                attempts = 0
                self.transaction_summary(account)



            elif choice in ["6","logout"]:
                attempts = 0
                print("Logged out.")

                break


            else:

                attempts =self.invalid_attempts(attempts)
            
    # =========================
    # LOGIN METHOD
    # =========================
    def login(self):
        print("\n--- LOGIN ---")
        account = self.authenticate()

        if account:
            print(
                f"\nWelcome "
                f"{self.accounts[account]['name']}"
            )
            
            self.user_menu(account)

    # =========================
    # TRANSACTIONS
    # =========================
    def add_transaction(self, acc, t_type, amount, details=""):
        entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": t_type,
            "amount": amount,
            "details": details
        }

        self.accounts[acc]["transactions"].append(entry)
        self.save_data()

    # =========================
    # CREATE ACCOUNT
    # =========================
    def create_account(self):
        print("\n--- Create Account ---")
        name = input("Enter name: ")

        attempts = 0
        
        while attempts < 3:
            pin = getpass("Create a 4-digit PIN: ")
            confirm = getpass("Confirm PIN: ")

            if pin != confirm:
                
                attempts += 1
                remaining = 3 - attempts
                
                print(
                    f"PINs do not match."
                    f"{remaining} attempts remaining.\n"
                )
                continue

            if not self.is_valid_pin(pin):
                
                attempts += 1
                
                remaining = 3 - attempts
                
                print(
                    f"PIN must be exactly 4 digits."
                    f"{remaining} attempts remaining.\n"
                )
                continue

            break
        
        if attempts == 3:
            print("\nToo many invalid PIN attempts.")
            print("Account creation cancelled.")
            return
        

        acc = self.generate_account_number()

        self.accounts[acc] = {
            "name": name,
            "pin": self.hash_pin(pin),
            "balance": 0.0,
            "transactions": [],
            "locked": False
        }

        self.save_data()

        print("\nAccount Created Successfully!")
        print(f"Account Number: {acc}")

    # =========================
    # DEPOSIT
    # =========================
    def deposit(self, acc):
        print("\n--- Deposit ---")
        
        attempts = 0
        while attempts < 3:
            try:
                
                amount = float(input("Enter amount: "))
            except ValueError:
                attempts += 1
                remaning = 3 - attempts
                print(f"Invalid input. Enter a number. {remaning} attempts remaining.\n")
                continue
            
            if amount <= 0:
                attempts += 1
                remaning = 3 - attempts
                print(f"Amount must be greater than 0. {remaning} attempts remaining.\n")
                continue
            

            self.accounts[acc]["balance"] += amount
            self.add_transaction(acc, "Deposit", amount)

            self.save_data()
            print("Deposit successful.")
            return
            
        print("\nToo many invalid attempts.")
        print("Deposit cancelled.")

    # =========================
    # WITHDRAW
    # =========================
    def withdraw(self, acc):
        print("\n--- Withdraw ---")

        attempts = 0
        while attempts < 3:
            
            try:
                amount = float(input("Enter amount: "))
            except ValueError:
                attempts += 1
                remaining = 3 - attempts
                print(f"Invalid input. Enter number. {remaining} attempts remaining.\n")
                continue
            if amount <= 0:
                attempts += 1
                remaining = 3 - attempts
                print("Invalid amount.")
                continue

            if amount > self.accounts[acc]["balance"]:
                print("Insufficient balance.")
                return
            
             
            while attempts < 3:
                pin = getpass("Enter PIN to confirm Withdrawal: ").strip()

                stored_hash = self.accounts[acc]["pin"]

                if self.verify_pin(pin, stored_hash):
                    break
                
                attempts += 1
                remaining = 3 - attempts
                
                if remaining > 0:
                    print(f"Wrong PIN. {remaining} attempts remaining.\n")
                else:
                    print("Too many incorrect PIN attempts. Account locked.")
                    self.accounts[acc]["locked"] = True
                    self.save_data()
                    return

            self.accounts[acc]["balance"] -= amount
            self.add_transaction(acc, "Withdraw", amount)

            self.save_data()
            print("Withdrawal successful.")
            return
        print("\nToo many invalid attempts.")
        print("Withdraw cancelled.")

    # =========================
    # TRANSFER
    # =========================
    def transfer(self, sender):
        print("\n--- Transfer ---")
        
        if self.accounts[sender].get("locked", False):
            print("Account is locked.")
            return
        
        attempts = 0
        while attempts < 3:
            pin = input("Enter PIN to confirm trnasfer: ").strip()

            stored_hash = self.accounts[sender]["pin"]

            if self.verify_pin(pin, stored_hash):
                break
            
            attempts += 1
            remaining = 3 - attempts
            
            if remaining > 0:
                print(f"Wrong PIN. {remaining} attempts remaining.\n")
            else:
                print("Too many incorrect PIN attempts. Account locked.")
                self.accounts[sender]["locked"] = True
                self.save_data()
                return
        
        receiver = input("Receiver Account Number: ")

        if receiver not in self.accounts:
            print("Receiver not found.")
            return

        attempts = 0
        while attempts < 3:
            try:
                
                amount = float(input("Enter amount: "))
            except ValueError:
                attempts += 1
                remaining = 3 -attempts
                print(f"Invalid input. Enter a number. {remaining} attempts remaining.\n")
                continue
            
            
            while attempts < 3:
                pin = input("Enter PIN to confirm trnasfer: ").strip()

                stored_hash = self.accounts[sender]["pin"]

                if self.verify_pin(pin, stored_hash):
                    break
                
                attempts += 1
                remaining = 3 - attempts
                
                if remaining > 0:
                    print(f"Wrong PIN. {remaining} attempts remaining.\n")
                else:
                    print("Too many incorrect PIN attempts. Account locked.")
                    self.accounts[sender]["locked"] = True
                    self.save_data()
                    return
            
            if amount <= 0:
                attempts += 1
                remaining = 3 - attempts
                print("Invalid amount.")
                continue

            if amount > self.accounts[sender]["balance"]:
                attempts += 1
                remaining = 3 - attempts
                print("Insufficient funds.")
                continue

            self.accounts[sender]["balance"] -= amount
            self.accounts[receiver]["balance"] += amount

            self.add_transaction(sender, "Transfer Sent", amount, f"To {receiver}")
            self.add_transaction(receiver, "Transfer Received", amount, f"From {sender}")

            self.save_data()
            print("Transfer successful.")
            return
    print("\nToo many invalid attempts.")
    print("Transfer Cancelled")

    # =========================
    # VIEW BALANCE
    # =========================
    def view_balance(self, acc):
        print("\n--- Balance ---")
        print(f"Name: {self.accounts[acc]['name']}")
        print(f"Balance: {self.accounts[acc]['balance']}")
    # =========================
    # TRANSACTIONS
    # =========================
    def transaction_summary(self, acc):
        print("\n--- Transactions ---")

        for i, t in enumerate(self.accounts[acc]["transactions"], 1):
            print(f"{i}. {t['time']} | {t['type']} | {t['amount']} | {t['details']}")

    # =========================
    # ADMIN DASHBOARD
    # =========================
    def admin_dashboard(self):
        print("\n--- ADMIN LOGIN ---")
        
        attempts = 0

        if not self.admin_login():
            print("Access denied.")
            return

        while True:
            print("\n===== ADMIN DASHBOARD =====")
            print("1. View All Accounts")
            print("2. View System Summary")
            print("3. Unlock Account")
            print("4. Exit Admin")

            choice = input("Select: ")

            if choice == "1":
                attempts = 0
                for acc, data in self.accounts.items():
                    print(f"{acc} | {data['name']} | Bal: {data['balance']} | Locked: {data.get('locked', False)}")

            elif choice == "2":
                attempts = 0
                print(f"Total Accounts: {len(self.accounts)}")

            elif choice == "3":
                attempts = 0
                acc = input("Enter account to unlock: ")
                if acc in self.accounts:
                    self.accounts[acc]["locked"] = False
                    self.save_data()
                    print("Account unlocked.")
                else:
                    print("Not found.")

            elif choice == "4":
                attempts = 0
                break
            
            else:
                attempts = self.invalid_attempts(attempts)

    # =========================
    # MENU
    # =========================
    def menu(self):

        attempts = 0

        while True:


            print("\n======================")
            print("OMAH'S BANKING SYSTEM")
            print("======================")



            print("1. Create Account")
            print("2. Login")
            print("3. Admin Dashboard")
            print("4. Exit")



            choice = input(
                "Select Option : "
            ).lower()



            if choice in ["1","create"]:
                attempts = 0
                self.create_account()



            elif choice in ["2","login"]:
                attempts = 0
                self.login()



            elif choice in ["3","admin"]:
                attempts = 0
                self.admin_dashboard()



            elif choice in ["4","exit"]:
                attempts = 0
                print("Thanks for Banking with us.")

                break



            else:

                attempts = self.invalid_attempts(attempts)


# =========================
# RUN SYSTEM
# =========================
if __name__ == "__main__":
    bank = BankingSystem()
    bank.menu()
    
    
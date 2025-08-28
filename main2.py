import mysql.connector
import random
import datetime
import hashlib


host = "localhost"
user = "root"              
password = "proven-stadium"  

connection = mysql.connector.connect(
    host=host,
    user=user,
    password=password
)

cursor = connection.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS bank")
cursor.execute("USE bank")

def TransactionDetails(acc):
    cursor.execute(f"SELECT * FROM Transactions WHERE FromAcc = {acc} OR ToAcc = {acc}")
    results = cursor.fetchall()
    for row in results:
        print(f'Transaction ID: {row[0]}, From Account: {row[1]}, To Account: {row[2]}, Amount: {row[3]}, Date: {row[4]}')

def AccountDetails(acc):
    cursor.execute(f"SELECT * FROM Persons WHERE AccountNumber = '{acc}'")
    result = cursor.fetchone()
    if not result:
        print("Account not found.")
        return
    print(f"""Account Number: {result[0]}
Name: {result[1]}
Balance: {result[5]}
Email: {result[3]}
Phone Number: {result[2]}
Account Type: {result[-2]}
Branch ID: {result[-1]}""")
    
        
def LoanInstallment(acc):
    cursor.execute(f"SELECT * FROM Loans WHERE AccountNumber = '{acc}'")
    results = cursor.fetchall()
    if len(results) == 0:
        print("No loans found for this account.")
        return
    for row in results:
        print(f'Loan ID: {row[0]}, Amount: {row[2]}, Interest Rate: {row[3]}, Duration: {row[4]}, Branch ID: {row[5]}, Status: {row[6]}')
    Loan_ID = input("Enter Loan ID to pay installment for, or type -1 to go back: ")
    if Loan_ID == '-1':
        return
    cursor.execute(f"SELECT Status FROM Loans WHERE LoanID = {Loan_ID} AND AccountNumber = '{acc}'")
    status = cursor.fetchone()[0]
    if status == 'Rejected' or status == 'Pending':
        print("Invalid Loan ID or Loan is not approved.")
        return
    elif status == 'Closed':
        print("Loan is already closed.")
        return
    cursor.execute(f"SELECT BankBalance FROM Persons WHERE AccountNumber = '{acc}'")
    balance = cursor.fetchone()[0]
    cursor.execute(f"SELECT Amount, InterestRate, Duration FROM Loans WHERE LoanID = {Loan_ID} AND AccountNumber = '{acc}'")
    loan = cursor.fetchone()
    monthly_installment = (loan[0]*((100 + loan[1])/100))/loan[2]
    if balance < monthly_installment:
        print("Insufficient funds to pay installment.")
        return

    cursor.execute(f'SELECT DueAmount FROM Loans WHERE LoanID = {Loan_ID}')
    dueamt = cursor.fetchone()[0]
    if dueamt <= monthly_installment:
        cursor.execute(f"UPDATE Loans SET Status = 'Closed', DueAmount = 0 WHERE LoanID = {Loan_ID}")
        cursor.execute(f"UPDATE Persons SET BankBalance = BankBalance - {dueamt} WHERE AccountNumber = '{acc}'")
        print("Loan fully paid and closed.")

def transfer(from_acc, to_acc, amount):
    cursor.execute(f"SELECT BankBalance FROM Persons WHERE AccountNumber={from_acc};")
    x = cursor.fetchall()
    if x[0][0] < amount:
        print("Insufficient funds")
        return
    cursor.execute(f"""INSERT INTO Transactions (FromAcc, ToAcc, Amount, DT)
VALUES ({from_acc},{to_acc},{amount},"{datetime.datetime.now().strftime('%H:%M:%S  %d %B %Y')}") ;""")
    cursor.execute(f"UPDATE Persons SET BankBalance=BankBalance-{amount} WHERE AccountNumber={from_acc};")
    cursor.execute(f"UPDATE Persons SET BankBalance=BankBalance+{amount} WHERE AccountNumber={to_acc};")
    connection.commit()

def CreateAccount():
    while True:
        Account_name = input("Enter bank account name, or type -1 to go back: ")
        if len(Account_name) > 100:
            print("Name is too long. Please enter a name with 100 characters or less.")
            continue
        elif Account_name == '-1':
            return
        break
    Account_password = hashlib.sha256(input("Enter account password: ").encode()).hexdigest()
    Account_Number = random.randint(50000000001, 99999999999)
    while True:    
        Account_Email = input("Enter email: ")
        if '@' in Account_Email and '.' in Account_Email:
            break
        else:
            print("Invalid email format. Please try again.")
    while True:
        Account_phoneno = input("Enter Phone Number: ")
        if len(Account_phoneno)==10:
            break
        else:
            print("Phone number must be 10 digits long. Please try again.")
    Account_Type = input("Enter account type (1 for Savings Account, 2 for Current Account): ")
    if Account_Type not in ['1', '2', '3']:
        print("Invalid account type. Account creation failed.")
        return main_menu
    print("""Select Branch ID from the following options:
          1. Main Branch, MG Road, Mumbai 400001
          2. City Center Branch, Park Street, Delhi 110001
          3. Tech Park Branch, Electronic City, Bangalore 560001
          4. Central Mall Branch, Anna Salai, Chennai 600001
          5. Lake View Branch, Salt Lake City, Kolkata 700001""")
    Branch_ID = input("Enter Branch ID (1-5): ")
    if Branch_ID not in ['1', '2', '3', '4', '5']:
        print("Invalid Branch ID. Account creation failed.")
        return main_menu
    if Account_Type == '1' or Account_Type == '2':
        Account_initial_Balance = input("Enter initial bank balance: ")

        cursor.execute(f"""
        INSERT INTO Persons 
        (Name, Password, AccountNumber, Email, PhoneNumber, BankBalance, AccountType, BranchID) 
        VALUES ("{Account_name}", "{Account_password}", {Account_Number}, "{Account_Email}", {Account_phoneno}, {Account_initial_Balance}, {Account_Type}, {Branch_ID});
        """)
    else:
        cursor.execute(f"""
        INSERT INTO Persons 
        (Name, Password, AccountNumber, Email, PhoneNumber, BankBalance, AccountType, Branch) 
        VALUES ("{Account_name}", "{Account_password}", {Account_Number}, "{Account_Email}", {Account_phoneno}, 0, "BM", {Branch_ID});
        """)
    connection.commit()

    print("Account saved.")
    print(f"Account created successfully! Your account number is {Account_Number}.")
    print("You can now log in with your account number and password.")



def ApplyLoan(acc):
    Amt = int(input("Enter loan amount: "))
    Duration = int(input("Enter duration (in months): "))
    Interest = float(input("Enter interest rate (in %): "))
    cursor.execute(f'INSERT INTO Loans (AccountNumber, Amount, InterestRate, Duration, BranchID, Status) VALUES ("{acc}", {Amt}, {Interest}, {Duration}, (SELECT BranchID FROM Persons WHERE AccountNumber="{acc}"), 2);')
    connection.commit()
    print("Loan application submitted successfully! Please wait for approval.")

def ApproveLoan(LoanID):
    cursor.execute(f'SELECT Amount, InterestRate FROM Loans WHERE LoanID={LoanID}')
    loan = cursor.fetchone()
    due_amount = loan[0] * (1 + loan[1]/100)  # Amount + Interest
    
    cursor.execute(f'UPDATE Loans SET Status="Approved", DueAmount={due_amount} WHERE LoanID={LoanID}')
    cursor.execute(f'INSERT into Transactions (ToAcc, Amount, DT) values ((select AccountNumber from Loans where LoanID={LoanID}), (select Amount from Loans where LoanID={LoanID}), "{datetime.datetime.now().strftime("%H:%M:%S  %d %B %Y")}");')
    cursor.execute(f'UPDATE Persons SET BankBalance=BankBalance+(select Amount from Loans where LoanID={LoanID}) where AccountNumber=(select AccountNumber from Loans where LoanID={LoanID});')
    connection.commit()
    print("Loan approved successfully!")
    print(f"Total amount due: {due_amount}")

def login():
    print("LOGIN")
    while True:
        account_number = input("Enter account number, or type -1 to go back: ")
        if account_number == '-1':
            return
        password = hashlib.sha256(input("Enter account password: ").encode()).hexdigest()
        cursor.execute(f"SELECT Password FROM Persons WHERE AccountNumber = '{account_number}'")
        if cursor.fetchone()[0]==password:
            break
        else:
            print("Invalid/Incorrect account number or password. Please try again.")
    cursor.execute(f"SELECT * FROM Persons WHERE AccountNumber = '{account_number}' AND Password = '{password}'")
    account = cursor.fetchone()
    if account!=None:
        print(f"Login successful! Welcome, {account[1]}!")
    else:
        print("Wrong Account Number or Password!")
        return main_menu
    if account[6] == 'S' or account[6] == 'C':
        while True:
            print("----------------------")
            print("1. Account Details")
            print("2. Transaction Details")
            print("3. Transfer Money")
            print("4. Update Account")
            print("5. Pay Loan Installment")
            print("6. Apply for Loan")
            print("7. Logout")
            print("8. Exit")
            choice = input("Enter your choice: ")

            if choice == '1':
                AccountDetails(account_number)
            elif choice == '2':
                TransactionDetails(account_number)
            elif choice == '3':
               transfer(account_number, input("Enter the account number to transfer to: "), int(input("Enter the amount to transfer: ")))
            elif choice == '4':
                while True:
                    print("----------------------")
                    print("1. Update Name")
                    print("2. Update Phone Number")
                    print("3. Update Email")
                    print("4. Update Password")
                    print("5. Update Account Type")
                    print("6. Go Back")
                    update_choice = input("Enter your choice: ")

                    if update_choice == '1':
                        new_name = input("Enter new name: ")
                        password = hashlib.sha256(input("Enter account password: ").encode()).hexdigest()
                        cursor.execute(f"SELECT Password FROM Persons WHERE AccountNumber = '{account_number}'")
                        if cursor.fetchone()[0] != password:
                            print("Incorrect password. Cannot update Name.")
                            continue
                        cursor.execute(f"UPDATE Persons SET Name = '{new_name}' WHERE AccountNumber = '{account_number}'")
                        connection.commit()
                        print("Name updated successfully.")
                    elif update_choice == '2':
                        while True:
                            new_phone = input("Enter new Phone Number: ")
                            if len(new_phone)==10:
                                break
                            else:
                                print("Phone number must be 10 digits long. Please try again.")
                                continue
                        password = hashlib.sha256(input("Enter account password to confirm: ").encode()).hexdigest()
                        cursor.execute(f"SELECT Password FROM Persons WHERE AccountNumber = '{account_number}'")
                        if cursor.fetchone()[0] != password:
                            print("Incorrect password. Cannot update Phone Number.")
                            continue
                        cursor.execute(f"UPDATE Persons SET PhoneNumber = '{new_phone}' WHERE AccountNumber = '{account_number}'")
                        connection.commit()
                        print("Phone number updated successfully.")
                    elif update_choice == '3':
                        while True:    
                            new_email = input("Enter new email: ")
                            if '@' in new_email and '.' in new_email:
                                break
                            else:
                                print("Invalid email format. Please try again.")
                                continue
                        password = hashlib.sha256(input("Enter account password to confirm: ").encode()).hexdigest()
                        cursor.execute(f"SELECT Password FROM Persons WHERE AccountNumber = '{account_number}'")
                        if cursor.fetchone()[0] != password:
                            print("Incorrect password. Cannot update Email.")
                            continue
                        cursor.execute(f"UPDATE Persons SET Email = '{new_email}' WHERE AccountNumber = '{account_number}'")
                        connection.commit()
                        print("Email updated successfully.")
                    elif update_choice == '4':
                        new_password = hashlib.sha256(input("Enter new account password : ").encode()).hexdigest()
                        password = hashlib.sha256(input("Enter old account password to confirm: ").encode()).hexdigest()
                        cursor.execute(f"SELECT Password FROM Persons WHERE AccountNumber = '{account_number}'")
                        if cursor.fetchone()[0] != password:
                            print("Incorrect password. Cannot update Password.")
                        cursor.execute(f"UPDATE Persons SET Password = '{new_password}' WHERE AccountNumber = '{account_number}'")
                        connection.commit()
                        print("Password updated successfully.")
                    elif update_choice == '5':
                        new_account_type = input("Enter new account type (0 for Savings, 1 for Current): ")
                        password = hashlib.sha256(input("Enter account password to confirm: ").encode()).hexdigest()
                        cursor.execute(f"SELECT Password FROM Persons WHERE AccountNumber = '{account_number}'")
                        if cursor.fetchone()[0] != password:
                            print("Incorrect password. Cannot update Account Type.")
                        cursor.execute(f"UPDATE Persons SET AccountType = {new_account_type} WHERE AccountNumber = '{account_number}'")
                        connection.commit()
                        print("Account type updated successfully.")
                    elif update_choice == '6':
                        break
                    else:
                        print("Invalid choice, please try again.")
            elif choice == '5':
                LoanInstallment(account_number)
            elif choice == '6':
                ApplyLoan(account_number)            
            elif choice == '7':
                print("Logged out")
                return main_menu
            elif choice == '8':
                print("Exiting the application.")
                cursor.close()
                connection.close()
                exit()

            else:
                print("Invalid choice, please try again.")
    elif account[6] == 'BM':
        while True:
            print("----------------------------------")
            print("1. Account Details")
            print("2. Branch Details")
            print("3. View All Accounts in Branch")
            print("4. View All Transactions in Branch")
            print("5. View All Loans in Branch")
            print("6. Approve Loan")
            print("7. Reject Loan")
            print("8. Logout")
            print("9. Exit")
            choice = input("Enter your choice: ")
            if choice == '1':
                AccountDetails(account_number)
            elif choice == '2':
                cursor.execute(f'select * from Branches where BranchID = {account[-1]}')
                print(cursor.fetchone())
            elif choice == '3':
                cursor.execute(f'select * from Persons where BranchID = {account[-1]}')
                for i in cursor.fetchall():
                    print(i)
            elif choice == '4':
                cursor.execute(f'select * from Transactions where FromAcc in (select AccountNumber from Persons where BranchID = {account[-1]}) or ToAcc in (select AccountNumber from Persons where BranchID = {account[-1]})')
                for i in cursor.fetchall():
                    print(i)
                cursor.execute(f'''SELECT SUM(Amount) FROM Transactions WHERE FromAcc in (select AccountNumber from Persons where BranchID={account[-1]}) or ToAcc in (select AccountNumber from Persons where BranchID={account[-1]})''')
                print("Branch Transaction Volume: ", cursor.fetchone()[0])

            elif choice == '5':
                cursor.execute(f'select * from Loans where BranchID = {account[-1]}')
                for i in cursor.fetchall():
                    print(i)
                cursor.execute(f'''SELECT SUM(Amount) FROM Loans WHERE Status="Approved" AND BranchID={account[-1]} GROUP BY BranchID''')
                print("Total Approved Loan Amount in your branch: ", cursor.fetchone()[0])
            elif choice == '6':
                LoanID = input("Enter Loan ID to approve: ")
                cursor.execute(f'select * from Loans where LoanID={LoanID} and Status="Pending" and BranchID={account[-1]}')
                x = cursor.fetchone()
                if x is None:
                    print("Invalid Loan ID or Loan is not pending or does not belong to your branch.")
                else:
                    print(x)
                    print('Are you sure you want to approve this loan? (y/n): ')
                    confirm = input().lower()
                    if confirm == 'y':
                        ApproveLoan(LoanID)
            elif choice == '7':
                LoanID = input("Enter Loan ID to reject: ")
                cursor.execute(f'select * from Loans where LoanID={LoanID} and Status="Pending" and BranchID={account[-1]}')
                x = cursor.fetchone()
                if x is None:
                    print("Invalid Loan ID or Loan is not pending or does not belong to your branch.")
                else:
                    print(x)
                    print('Are you sure you want to reject this loan? (y/n): ')
                    confirm = input().lower()
                    if confirm == 'y':
                        cursor.execute(f'UPDATE Loans SET Status="Rejected" WHERE LoanID={LoanID};')
                        connection.commit()
                        print("Loan rejected successfully!")
            elif choice == '8':
                print("Logged out")
                return main_menu
            elif choice == '9':
                print("Exiting the application.")
                cursor.close()
                connection.close()
                exit()
    


def main_menu():
    while True:
        print("-----------------")
        print("1. Create Account")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter the choice: ")
        if choice == '1':
            CreateAccount()
        elif choice == '2':
            login()
        elif choice == '3':
            print("Exiting the application.")
            cursor.close()
            connection.close()
            exit()
        else:
            print("Choice is invalid, please try again.")


cursor.execute("""CREATE TABLE IF NOT EXISTS Branches(
    BranchID int PRIMARY KEY AUTO_INCREMENT,
    Address varchar(100)
);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS Persons(
    AccountNumber char(11) PRIMARY KEY,
    Name varchar(100),
    PhoneNumber char(10),
    Email varchar(150),
    Password varchar(150),
    BankBalance float(22,2),
    AccountType enum("S", "C", "BM","Admin"),  
    BranchID int,
    Foreign Key (BranchID) REFERENCES Branches(BranchID)
);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS Loans(
    LoanID int PRIMARY KEY AUTO_INCREMENT,
    AccountNumber char(11),
    Amount float(22,2),
    InterestRate float(5,2),
    Duration int,
    BranchID int,
    Status enum("Approved", "Pending", "Rejected", "Closed"),
    DueAmount float(22,2) DEFAULT 0,
    Foreign Key (BranchID) REFERENCES Branches(BranchID),
    Foreign Key (AccountNumber) REFERENCES Persons(AccountNumber)          
);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS Transactions (
    TransactionID int NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
    FromAcc char(11),
    ToAcc char(11),
    Amount integer NOT NULL CHECK (Amount>0),
    DT varchar(50),
    FOREIGN KEY (FromAcc) REFERENCES Persons(AccountNumber),
    FOREIGN KEY (ToAcc) REFERENCES Persons(AccountNumber)
);""")

cursor.execute("SELECT COUNT(*) FROM Branches")
if cursor.fetchone()[0] == 0:
    cursor.execute("""
    INSERT INTO Branches (Address) VALUES 
        ('Main Branch, MG Road, Mumbai 400001'),
        ('City Center Branch, Park Street, Delhi 110001'),
        ('Tech Park Branch, Electronic City, Bangalore 560001'),
        ('Central Mall Branch, Anna Salai, Chennai 600001'),
        ('Lake View Branch, Salt Lake City, Kolkata 700001');
    """)
    connection.commit()

while True:
    main_menu()

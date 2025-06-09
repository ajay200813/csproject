import mysql.connector
import random
import datetime


host = "localhost"
user = "root"              
password = "proven-stadium"  

connection = mysql.connector.connect(
    host=host,
    user=user,
    password=password
)

cursor = connection.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS CSPROJECT")
cursor.execute("USE CSPROJECT")

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
    if result[-1]==0:
        s='Savings Account'
    elif result[-1]==1:
        s='Current Account'
    elif result[-1]==2:
        s='Bank Manager'
    if result[-1]==0 or result[-1]==1:
        print(f"""Account Number: {result[0]}
Name: {result[1]}
Balance: {result[5]}
Email: {result[3]}
Phone Number: {result[2]}
Account Type: {s}""")
    elif result[-1]==2:
        print(f"""Account Number: {result[0]}
Name: {result[1]}
Email: {result[3]}
Phone Number: {result[2]}
Account Type: {s}""")
        

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
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS CSPROJECT")
    cursor.execute("USE CSPROJECT")
    cursor.execute("""CREATE TABLE IF NOT EXISTS Persons (
        AccountNumber char(11) PRIMARY KEY,
        Name varchar(100),
        PhoneNumber char(10),
        Email varchar(150),
        Password varchar(150),
        BankBalance float(22,2),
        AccountType varchar(20)
    );""")

    while True:
        Account_name = input("Enter bank account name, or type -1 to go back: ")
        if len(Account_name) > 100:
            print("Name is too long. Please enter a name with 100 characters or less.")
            continue
        elif Account_name == '-1':
            return
        break
    Account_password = input("Enter account password: ")
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
            

    Account_initial_Balance = input("Enter initial bank balance: ")
    Account_Type = input("Enter account type (0 for Savings Account, 1 for Current Account): ")

    cursor.execute(f"""
    INSERT INTO Persons 
    (Name, Password, AccountNumber, Email, PhoneNumber, BankBalance, AccountType) 
    VALUES ("{Account_name}", "{Account_password}", {Account_Number}, "{Account_Email}", {Account_phoneno}, {Account_initial_Balance}, {Account_Type});
    """)
    connection.commit()

    print("Account saved.")
    print(f"Account created successfully! Your account number is {Account_Number}.")
    print("You can now log in with your account number and password.")





def login():
    cursor = connection.cursor()
    cursor.execute("USE CSPROJECT")
    
    print("LOGIN")
    while True:
        account_number = input("Enter account number, or type -1 to go back: ")
        if account_number == '-1':
            return
        password = input("Enter password: ")
        cursor.execute(f"SELECT Password FROM Persons WHERE AccountNumber = '{account_number}'")
        if cursor.fetchone()[0]==password:
            break
        else:
            print("Invalid/Incorrect account number or password. Please try again.")
    cursor.execute(f"SELECT * FROM Persons WHERE AccountNumber = '{account_number}' AND Password = '{password}'")
    account = cursor.fetchone()
    if account!=None:
        print(f"Login successful! Welcome, {account[1]}!")
    while True:
        print("1. Account Details")
        print("2. Transaction Details")
        print("3. Transfer Money")
        print("4. Update Account")
        print("5. Logout")
        print("6. Exit")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            AccountDetails(account_number)
        elif choice == '2':
            TransactionDetails(account_number)
        elif choice == '3':
           transfer(account_number, input("Enter the account number to transfer to: "), int(input("Enter the amount to transfer: ")))
        elif choice == '4':
            while True:
                print("1. Update Name")
                print("2. Update Phone Number")
                print("3. Update Email")
                print("4. Update Password")
                print("5. Update Account Type")
                print("6. Go Back")
                update_choice = input("Enter your choice: ")
                
                if update_choice == '1':
                    new_name = input("Enter new name: ")
                    password = input("Enter your password to confirm: ")
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
                    password = input("Enter your password to confirm: ")
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
                    password = input("Enter your password to confirm: ")
                    cursor.execute(f"SELECT Password FROM Persons WHERE AccountNumber = '{account_number}'")
                    if cursor.fetchone()[0] != password:
                        print("Incorrect password. Cannot update Email.")
                        continue
                    cursor.execute(f"UPDATE Persons SET Email = '{new_email}' WHERE AccountNumber = '{account_number}'")
                    connection.commit()
                    print("Email updated successfully.")
                elif update_choice == '4':
                    new_password = input("Enter new password: ")
                    password = input("Enter your password to confirm: ")
                    cursor.execute(f"SELECT Password FROM Persons WHERE AccountNumber = '{account_number}'")
                    if cursor.fetchone()[0] != password:
                        print("Incorrect password. Cannot update Password.")
                    cursor.execute(f"UPDATE Persons SET Password = '{new_password}' WHERE AccountNumber = '{account_number}'")
                    connection.commit()
                    print("Password updated successfully.")
                elif update_choice == '5':
                    new_account_type = input("Enter new account type (0 for Savings, 1 for Current): ")
                    password = input("Enter your password to confirm: ")
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
            print("Logged out")
            return main_menu
        elif choice == '6':
            print("Exiting the application.")
            cursor.close()
            connection.close()
            exit()
        
        else:
            print("Invalid choice, please try again.")
    else:
        print("Wrong Account Number or Password!")



def main_menu():
    while True:
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



cursor.execute("""CREATE TABLE IF NOT EXISTS Persons(
    AccountNumber char(11) PRIMARY KEY,
    Name varchar(100),
    PhoneNumber char(10),
    Email varchar(150),
    Password varchar(150),
    BankBalance float(22,2),
    AccountType int  # Changed to varchar to accept 'FD', 'SA', etc.
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


while True:
    main_menu()
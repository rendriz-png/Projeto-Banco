from dataclasses import dataclass, asdict
from typing import List, Any
from datetime import date
import csv
import random
import os
import sys
import getpass

# ========================== DATA CLASSES ==========================
@dataclass
class Operator:
    operator_id: str    # 5 digits
    operator_password: str
    operator_name: str
    access_level: int  # 0 to 5


@dataclass
class Transaction:
    transaction_type: str  # "Deposit", "Withdraw", "Loan" , "Paid Loan"
    transaction_name: str   # so the client understand what transaction it is
    transaction_date: date
    interest_rate: float
    interest: float
    amount: float
    operator_id: str        
    client_acc_number: str
    Transaction_id: str
    original_amount: float


@dataclass
class Client:
    client_id: str # 12 digits numbers only
    client_name: str
    acc_number: str # 8 digigts numbers only
    agency_number: str # 4 digits numbers only
    creation_date: date
    client_password: str
    balance: float
    debt: float

# ====== UTILITY FUNCTIONS ======
def get_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt).strip())
            return value
        except ValueError:
            print("Invalid input. Please enter numbers only:")

def get_float(prompt: str) -> float:
    while True:
        user_input = input(prompt).strip()
        user_input = user_input.replace(",", ".")  # Replace comma with dot
        try:
            value = float(user_input)
            return value
        except ValueError:
            print("Invalid input. Please enter a valid number (use , or . for decimals).")

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_random_number(digits: int) -> str:
    return str(random.randint(0, 10**digits - 1)).zfill(digits)

def search_index(data_list: List[Any], field_name: str, value: str) -> int:
    for i, item in enumerate(data_list):
        if getattr(item, field_name) == value:
            return i
    return -1


def months_between(start_date: date, end_date: date) -> int:
    return abs((end_date.year - start_date.year) * 12 + (end_date.month - start_date.month))

def calculate_loan_debt(transaction: Transaction) -> float:
    """
    Calculate the current debt for a loan transaction using compound interest.
    
    :param transaction: A Transaction object (must be of type "Loan")
    :return: Current debt value
    """
    if transaction.transaction_type.lower() != "loan":
        return 0.0  # Not a loan, no debt to calculate
    
    # Principal (loan amount)
    principal = transaction.amount
    
    # Annual interest rate (as decimal, e.g. 0.05 = 5%)
    rate = transaction.interest_rate
    
    # Time in months since loan date
    today = date.today()
    months_passed = (today.year - transaction.transaction_date.year) * 12 + (today.month - transaction.transaction_date.month)
    
    if months_passed <= 0:
        return principal  # No time has passed
    
    # Compound interest monthly
    compounds_per_year = 12
    time_years = months_passed / 12
    
    # Final debt
    debt = principal * (1 + rate / compounds_per_year) ** (compounds_per_year * time_years)
    
    return round(debt, 2)



# ====== CSV HANDLING ======
def ensure_csv_exists(file_path: str, headers: list[str]) -> None:
    """Check if CSV exists; if not, create it with headers."""
    if not os.path.exists(file_path):
        with open(file_path, mode="w", newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()

def save_to_csv(file_path: str, data_list: list) -> None:
    if not data_list:
        print("No data to save.")
        return
    fieldnames = data_list[0].__dataclass_fields__.keys()
    with open(file_path, mode="w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in data_list:
            writer.writerow(asdict(item))


# ====== LOADERS ======
def load_operators(file_path: str) -> List[Operator]:
    operators = []
    with open(file_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            operators.append(
                Operator(
                    operator_id=row["operator_id"],
                    operator_password=row["operator_password"],
                    operator_name=row["operator_name"],
                    access_level=int(row["access_level"])
                )
            )
    return operators

def load_clients(file_path: str) -> List[Client]:
    clients = []
    with open(file_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            clients.append(
                Client(
                    client_id=row["client_id"],
                    client_name=row["client_name"],
                    acc_number=row["acc_number"],
                    agency_number=row["agency_number"],
                    creation_date=date.fromisoformat(row["creation_date"]),
                    client_password=row["client_password"],
                    balance=float(row["balance"]),
                    debt=float(row["debt"])
                )
            )
    return clients

def load_transactions(file_path: str) -> List[Transaction]:
    transactions = []

    with open(file_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            transactions.append(
                Transaction(
                    transaction_type=row["transaction_type"],
                    transaction_name=row["transaction_name"],
                    transaction_date=date.fromisoformat(row["transaction_date"]),
                    interest_rate=float(row["interest_rate"]),
                    interest=float(row["interest"]),
                    amount=float(row["amount"]),
                    operator_id=row["operator_id"],
                    client_acc_number=row["client_acc_number"],
                    Transaction_id=row["Transaction_id"],
                    original_amount=float(row["original_amount"])
                )
            )
    return transactions


# ====== OPERATORS ======
def check_operator_login(operator_check: Operator, operator_database: List[Operator]) -> bool:
    for operator in operator_database:
        if operator.operator_id == operator_check.operator_id and operator.operator_password == operator_check.operator_password:
            return True
    return False

def operator_login(operators: list[Operator]) -> Operator:
    while True:
        temp_operator_id=input("Enter operator ID: ").strip()
        clear_terminal()
        password=getpass.getpass("Enter operator password: ")
        clear_terminal()
        active_operator = Operator(
            operator_id=temp_operator_id,
            operator_password=password,
            operator_name="",
            access_level=0
        )

        if check_operator_login(active_operator, operators):
            print("Login successful!")
            break
        else:
            print("Invalid login, please try again.")

    for operator in operators:
        if active_operator.operator_id == operator.operator_id:
            active_operator = operator
            break

    return active_operator

def change_operator_level(operators:List[Operator]): 
    clear_terminal()
    operator_id=input("insert operator ID:").strip()
    index=search_index(operators,"operator_id",operator_id)
    if index== -1:
        print(f"operator not found")
        return
    desired_level=0
    while desired_level not in (1, 2, 3, 4, 5):
        desired_level=get_int("insert the disered access level:(1 to 5)")
        if desired_level not in (1, 2, 3, 4, 5):
            print(f"Invalid option try again:(1 to 5)")
        else:
            operators[index].access_level=desired_level
    print(f"New operator access level:{operators[index].access_level}")
    

def print_operator_data(operator:Operator):
    print("=" * 40)
    print(f"Operator ID:   {operator.operator_id}")
    print(f"Operator name: {operator.operator_name}")
    print(f"Operator access level:  {operator.access_level}")
    print("=" * 40)

def register_new_operator(operators:List[Operator]):
    control=0
    while(control!=-1):
        new_id=generate_random_number(5)
        control=search_index(operators,"operator_id",new_id)
    new_operator=Operator( 
        operator_id=new_id,
        operator_password=getpass.getpass("enter new operator password:").strip(),
        operator_name=input("enter new operator Name:").strip().title(),
        access_level=get_int("enter new operator access level:")
    )
    operators.append(new_operator)
    clear_terminal()
    print(f"New operator registerd")
    print_operator_data(operators[-1])


# ====== CLIENTS ======
def check_acc_number_availability(client_database: List[Client], acc_number: str) -> bool:
    for client in client_database:
        if acc_number == client.acc_number:
            return False
    return True

def search_client(client_search: str, clients: List[Client]) -> Client | None:
    for client in clients:
        if client.acc_number == client_search or client.client_id == client_search or client_search.title() == client.client_name:
            return client
    return None

def print_client_data(client: Client) -> None:
    print("=" * 40)
    print(f"Client ID     : {client.client_id}")
    print(f"Name          : {client.client_name}")
    print(f"Account Number: {client.acc_number}")
    print(f"Agency Number : {client.agency_number}")
    print(f"Created On    : {client.creation_date}")
    print(f"Balance       : ${client.balance:,.2f}")
    print(f"Debt          : ${client.debt:,.2f}")
    print("=" * 40)

def create_new_client(clients: List[Client]):
    new_client = Client(
        client_id=input("Insert client ID: ").strip(),
        client_name=input("Insert client's name: ").title().strip(),
        acc_number="",
        agency_number=str(get_int("Insert agency number: ")).strip(),
        creation_date=date.today(),
        client_password=input("Insert client password: ").strip(),
        balance=0.0,
        debt=0.0
    )
    while True:
        temp_number = generate_random_number(8)
        if check_acc_number_availability(clients, temp_number):
            new_client.acc_number = temp_number
            break
    clients.append(new_client)
    print("New client registered:\n")
    print_client_data(new_client)
    input("Press Enter to continue...")

def remove_client(clients: List[Client], acc_number: str):
    index = search_index(clients, "acc_number", acc_number)
    if index != -1:
        if(clients[index].debt==0):
            clients.pop(index)
            print(f"Client with account {acc_number} removed.")

        else:
            print(f"Client in debt, pay the debt before removing this account")
    else:
        print(f"No client found with account number {acc_number}.")
    input("press Enter to continue...")

def check_client_login(client_check: Client, client_database: List[Client]) -> bool:
    for client in client_database:
        if client.acc_number == client_check.acc_number and client.client_password == client_check.client_password:
            return True
    return False

def client_login(clients: List[Client]) -> Client:
    while True:
        acc_number=input("Insert client's account number: ").strip()
        clear_terminal()
        password=getpass.getpass("Enter client password: ")
        active_client = Client(
            client_id="",
            client_name="",
            acc_number=acc_number,
            agency_number="",
            creation_date=date.today(),
            client_password=password,
            balance=0,
            debt=0,
        )
        if check_client_login(active_client, clients):
            print("Login successful!")
            break
        else:
            print("Invalid login, please try again.")

    for client in clients:
        if active_client.acc_number == client.acc_number:
            active_client = client
            break
    return active_client


# ====== TRANSACTIONS ======
def generate_unique_transaction_id(transactions: List[Transaction]) -> str:
    while True:
        temp_id = generate_random_number(12)
        if all(temp_id != t.Transaction_id for t in transactions):
            return temp_id

def search_transaction(transactions: List[Transaction], transaction_id: str) -> Transaction | None:
    """Search for a transaction by its ID."""
    for transaction in transactions:
        if transaction.Transaction_id == transaction_id:
            return transaction
    return None

def print_transaction_data(transaction: Transaction) -> None:
    amount=transaction.amount+transaction.interest
    print("=" * 40)
    print(f"Transaction ID   : {transaction.Transaction_id}")
    print(f"Type             : {transaction.transaction_type}")
    if transaction.transaction_name:
        print(f"Name             : {transaction.transaction_name}")
    print(f"Date             : {transaction.transaction_date}")
    print(f"Total amount     : ${amount:,.2f}")

    # Only show interest info if it's a Loan
    if transaction.transaction_type.lower() == "loan":
        print(f"Interest         : ${transaction.interest:,.2f}")
        print(f"Interest Rate    : {transaction.interest_rate:.2f}%")
        print(f"Original Amount  : ${transaction.original_amount:,.2f}")

    print(f"Operator ID      : {transaction.operator_id}")
    print(f"Client Account   : {transaction.client_acc_number}")
    print("=" * 40)

def update_debt(clients: List[Client], transactions: List[Transaction], control: int):
    for client in clients:
        total_debt = 0.0  # reset for each client
        for transaction in transactions:
            if (client.acc_number == transaction.client_acc_number and transaction.transaction_type == "Loan"):
                total_debt += calculate_loan_debt(transaction)
            if(transaction.transaction_type == "Loan" or transaction.transaction_type=="loan"):
                transaction.interest=calculate_loan_debt(transaction)-transaction.amount
        client.debt = round(total_debt, 2)  # update client's debt
        
    if control == 0:
        return clients
    elif control == 1:
        return transactions


# ─────────────────────────────
# Client session actions
# ─────────────────────────────
def do_deposit(clients, transactions, active_client, active_operator, program_path):
    clear_terminal()
    deposit = get_float("What amount to deposit? ")
    idx = search_index(clients, "acc_number", active_client.acc_number)

    clients[idx].balance += deposit
    transaction_id = generate_unique_transaction_id(transactions)

    transaction = Transaction(
        transaction_type="Deposit",
        transaction_name=input("Insert a tag (optional): ").strip().title() or "Deposit",
        transaction_date=date.today(),
        interest_rate=0.00,
        interest=0.0,
        amount=deposit,
        operator_id=active_operator.operator_id,
        client_acc_number=active_client.acc_number,
        Transaction_id=transaction_id,
        original_amount=deposit
    )

    transactions.append(transaction)
    clear_terminal()
    print_transaction_data(transaction)
    print(f"New balance is: ${clients[idx].balance:,.2f}")

    save_to_csv(f"{program_path}/clients.csv", clients)
    save_to_csv(f"{program_path}/transactions.csv", transactions)
    input("Press Enter to continue...")


def do_withdraw(clients, transactions, active_client, active_operator, program_path):
    clear_terminal()
    withdraw = get_float("What amount to withdraw? ")
    idx = search_index(clients, "acc_number", active_client.acc_number)

    if withdraw > clients[idx].balance:
        print("Insufficient funds.")
    else:
        clients[idx].balance -= withdraw
        transaction_id = generate_unique_transaction_id(transactions)

        transaction = Transaction(
            transaction_type="Withdraw",
            transaction_name=input("Insert a tag (optional): ").title().strip() or "Withdraw",
            transaction_date=date.today(),
            interest_rate=0.00,
            interest=0.0,
            amount=withdraw,
            operator_id=active_operator.operator_id,
            client_acc_number=active_client.acc_number,
            Transaction_id=transaction_id,
            original_amount= withdraw
        )
        clear_terminal()
        transactions.append(transaction)
        print_transaction_data(transaction)
        print(f"New balance is: ${clients[idx].balance:,.2f}")

        save_to_csv(f"{program_path}/clients.csv", clients)
        save_to_csv(f"{program_path}/transactions.csv", transactions)
    input("Press Enter to continue...")


def do_loan(clients, transactions, active_client, active_operator, program_path):
    clear_terminal()
    loan = get_float("What amount to loan? ")
    interest_rate = get_float("please input the autorized interest rate: ")
    interest = 0.00
    idx = search_index(clients, "acc_number", active_client.acc_number)

    clients[idx].balance += loan
    clients[idx].debt += loan + interest
    transaction_id = generate_unique_transaction_id(transactions)

    transaction = Transaction(
        transaction_type="Loan",
        transaction_name=input("Insert a tag (optional): ").strip().title() or "Loan",
        transaction_date=date.today(),
        interest_rate=interest_rate,
        interest=interest,
        amount=loan,
        operator_id=active_operator.operator_id,
        client_acc_number=active_client.acc_number,
        Transaction_id=transaction_id,
        original_amount=loan
    )

    transactions.append(transaction)
    print(f"Loan granted: ${loan:,.2f} with interest ${interest:,.2f}")
    print(f"New balance is: ${clients[idx].balance:,.2f}")
    print(f"Total debt is: ${clients[idx].debt:,.2f}")
    print_transaction_data(transaction)

    save_to_csv(f"{program_path}/clients.csv", clients)
    save_to_csv(f"{program_path}/transactions.csv", transactions)
    input("Press Enter to continue...")


def pay_loan(clients, transactions, active_client, active_operator, program_path):
    clear_terminal()
    temp_transaction = input("Please enter transaction ID: ").strip()
    active_transaction = search_transaction(transactions, temp_transaction)

    if not active_transaction:
        print("Transaction not found.")
        input("Press Enter to continue...")
        return

    loan_debt = active_transaction.amount + active_transaction.interest
    print(f"Your debt in this loan is ${loan_debt:,.2f}")

    redemption = get_float("What amount do you want to pay? ")
    if redemption > active_client.balance:
        print(f"Insufficient funds. Your balance is ${active_client.balance:,.2f}")
        input("Press Enter to continue...")
        return

    idx_client = search_index(clients, "acc_number", active_client.acc_number)
    idx_transaction = search_index(transactions, "Transaction_id", active_transaction.Transaction_id)

    if redemption < loan_debt:
        clients[idx_client].balance -= redemption
        clients[idx_client].debt -= redemption
        transactions[idx_transaction].amount-= redemption

        transaction_id = generate_unique_transaction_id(transactions)
        new_transaction = Transaction(
            transaction_type="Loan Payment",
            transaction_name=active_transaction.transaction_name,
            transaction_date=date.today(),
            interest_rate=transactions[idx_transaction].interest_rate,
            interest=0.0,
            amount=redemption,
            operator_id=active_operator.operator_id,
            client_acc_number=active_client.acc_number,
            Transaction_id=transaction_id,
            original_amount=active_transaction.original_amount
        )
        transactions.append(new_transaction)

    elif redemption == loan_debt:
        clients[idx_client].balance -= redemption
        clients[idx_client].debt -= redemption
        transactions[idx_transaction].transaction_type = "Paid Loan"
        new_transaction = Transaction(
            transaction_type="Loan Payment",
            transaction_name=active_transaction.transaction_name,
            transaction_date=date.today(),
            interest_rate=transactions[idx_transaction].interest_rate,
            interest=0.0,
            amount=redemption,
            operator_id=active_operator.operator_id,
            client_acc_number=active_client.acc_number,
            Transaction_id=transaction_id,
            original_amount=active_transaction.original_amount
        )
        transactions.append(new_transaction)
        print("Payment recived:")
        print_transaction_data(new_transaction)
    else:
        print("Value higher than debt, try again.")
        input("Press Enter to continue...")
        return

    save_to_csv(f"{program_path}/clients.csv", clients)
    save_to_csv(f"{program_path}/transactions.csv", transactions)
    input("Press Enter to continue...")


# ─────────────────────────────
# Submenus
# ─────────────────────────────
def client_session(clients, transactions, active_client, active_operator, program_path):
    while True:
        clear_terminal()
        control = input(
            "What do you wish to do?:\n"
            "1-Deposit\n"
            "2-Withdraw\n"
            "3-Loan\n"
            "4-Check info\n"
            "5-Pay loan\n"
            "6-Go back\n"
        )
        match control:
            case "1": 
                if(active_operator.access_level>0):
                    do_deposit(clients, transactions, active_client, active_operator, program_path)
                else:
                    print("Access denied: low access level")
                    input("Press Enter to continue...")
            case "2": 
                if(active_operator.access_level>0):
                    do_withdraw(clients, transactions, active_client, active_operator, program_path)
                else:
                    print("Access denied: low access level")
                    input("Press Enter to continue...")
            case "3": 
                if(active_operator.access_level>1):
                    do_loan(clients, transactions, active_client, active_operator, program_path)
                else:
                    print("Access denied: low access level")
                    input("Press Enter to continue...")
            case "4":
                clear_terminal()
                print_client_data(active_client)
                for transaction in transactions:
                    if active_client.acc_number == transaction.client_acc_number:
                        print_transaction_data(transaction)
                input("Press Enter to continue...")
            case "5": 
                if(active_operator.access_level>0):
                    pay_loan(clients, transactions, active_client, active_operator, program_path)
                else:
                    print("Access denied: low access level")
                    input("Press Enter to continue...")
            case "6": break
            case _: 
                print("Invalid option, try again.")
                input("Press Enter to continue...")


def client_operations(clients, transactions, active_operator, program_path):
    while True:
        clear_terminal()
        control = input(
            "Which action to execute?:\n"
            "1-Register new client\n"
            "2-Remove client\n"
            "3-Log-in client\n"
            "4-Return to main menu\n"
            "5-Exit Application\n"
        )
        match control:
            case "1":
                create_new_client(clients)
                save_to_csv(f"{program_path}/clients.csv", clients)
            case "2":
                if active_operator.access_level < 3:
                    print("Access denied: low access level")
                    input("Press Enter to continue...")
                else:
                    ex_client_acc = input("Insert account number to delete: ").strip()
                    remove_client(clients, ex_client_acc)
                    save_to_csv(f"{program_path}/clients.csv", clients)
            case "3":
                active_client = client_login(clients)
                client_session(clients, transactions, active_client, active_operator, program_path)
            case "4": break
            case "5":
                print("Exiting application...")
                exit()
            case _:
                print("Invalid option, try again.")
                input("Press Enter to continue...")


def operator_operations(operators, active_operator,program_path):
    if active_operator.access_level >= 2:
        while True:
            clear_terminal()
            control = input(
                "Which action to execute?:\n"
                "1-Register operator\n"
                "2-Remove operator\n"
                "3-Change operator access level\n"
                "4-Return to main menu\n"
                "5-Exit Application\n"
        )
            clear_terminal()
            match control:
                case "1":
                    if active_operator.access_level >= 3:
                        register_new_operator(operators)
                        save_to_csv(f"{program_path}/operators.csv",operators)
                    else:    
                        print("Access denied: low access level")
                    input("press Enter to continue...")
                case "2":
                    if active_operator.access_level >= 4:
                        operator_delete_id=input("Insert operator ID to delete:").strip()
                        operator_index=search_index(operators,"operator_id",operator_delete_id)
                        if operator_index != -1:
                            operators.pop(operator_index)
                            save_to_csv(f"{program_path}/operators.csv",operators)
                        else:
                            print(f"Operator not found")
                    else:
                        print("Access denied: low access level")
                    input("press Enter to continue...")
                case "3":
                    if active_operator.access_level >= 4:
                        change_operator_level(operators)
                        save_to_csv(f"{program_path}/operators.csv",operators)
                    else:
                        print("Access denied: low access level")
                    input("press Enter to continue...")
                case "4":
                    break
                case "5":
                    print("You will now exit")
                    exit()
                
                case _:
                    print("Invalid option, try again.")
                    input("Press Enter to continue...")  
    else:
        print("Access denied, insufficient access level.")
        input("Press Enter to continue...")


# ─────────────────────────────
# Main menu
# ─────────────────────────────
def main_menu(clients, operators, transactions, program_path, active_operator):
   
    while True:
        clear_terminal()
        control = input(
            "What operation do you want to execute?:\n"
            "1-Access client data\n"
            "2-Access operator data\n"
            "3-Log-off\n"
            "4-Exit\n"
        )
        clear_terminal()
        match control:
            case "1":
                if active_operator.access_level >= 1:
                    client_operations(clients, transactions, active_operator, program_path)
                else:
                    print("Access denied, call a superior")
                    input("Press Enter to continue...")
            case "2": 
                if active_operator.access_level >= 1:
                    operator_operations(operators, active_operator,program_path)
            case "3":
                print("Logging off...")
                clear_terminal()
                active_operator = operator_login(operators)
            case "4":
                print("You will now exit")
                exit()
            case _:
                print("Invalid command, try again")
                input("Press Enter to continue...")



# ====== MAIN PROGRAM ======
if getattr(sys, 'frozen', False):
    program_path = os.path.dirname(sys.executable)
else:
    program_path = os.path.dirname(os.path.abspath(__file__))

# Ensure CSVs exist
if not os.path.exists(os.path.join(program_path, "operators.csv")):
    csv_found=False
    print("No operetors found, Please proced to register")
    input("Press Enter to continue...")
    emergency_op:list[Operator]=[]
    clear_terminal()
    register_new_operator(emergency_op)
    input("Press Enter to continue ...")
    active_operator=emergency_op[0]
else:
    csv_found=True
ensure_csv_exists(os.path.join(program_path, "operators.csv"), list(Operator.__dataclass_fields__.keys()))
ensure_csv_exists(os.path.join(program_path, "clients.csv"), list(Client.__dataclass_fields__.keys()))
ensure_csv_exists(os.path.join(program_path, "transactions.csv"), list(Transaction.__dataclass_fields__.keys()))



# Load data
operators: List[Operator] = load_operators(os.path.join(program_path, "operators.csv"))
clients: List[Client] = load_clients(os.path.join(program_path, "clients.csv"))
transactions: List[Transaction] = load_transactions(os.path.join(program_path, "transactions.csv"))
if (csv_found == False ):
    operators.append(active_operator)
    save_to_csv(f"{program_path}/operators.csv",operators)
# Update debts
update_debt(clients, transactions, 0)

# Operator login
if csv_found == True:
    active_operator = operator_login(operators)
    input("Press Enter to continue...")
clear_terminal()
main_menu(clients, operators, transactions, program_path, active_operator)


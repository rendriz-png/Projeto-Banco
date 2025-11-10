from dataclasses import dataclass
from typing import List
from datetime import date
import csv
import time
import random

@dataclass
class Operator:
    operator_id: str
    operator_password: str
    operator_name: str
    access_level: int  # 0 to 5 where 5 is the strongest

@dataclass
class Transaction:
    transaction_type: str  # "Deposit", "Withdraw", "Loan"
    transaction_name: str
    transaction_date: date
    interest_rate: float
    interest: float
    amount: float
    operator_id: str
    client_id: str
    Transaction_id: str

@dataclass
class Client:
    client_id: str
    client_name: str
    acc_number: str
    agency_number: str
    creation_date: date
    client_password: str
    balance: float
    debt: float

def check_acc_number_availability(client_database: List[Client], acc_number: str) -> bool:
    for client in client_database:
        if acc_number == client.acc_number:
            return False
    return True

def get_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("Invalid input. Please enter numbers only:")

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
                    access_level=int(row["acces_lvl"])
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
                    client_id=row["client_id"],
                    Transaction_id=row["Transaction_id"]
                )
            )
    return transactions

def check_operator_login(operator_check: Operator, operator_database: List[Operator]) -> bool:
    for operator in operator_database:
        if operator.operator_id == operator_check.operator_id and operator.operator_password == operator_check.operator_password:
            return True
    return False

def search_client(client_search: str, clients: List[Client]) -> Client | None:
    for client in clients:
        if client.acc_number == client_search or client.client_id == client_search:
            return client
    return None

def generate_random_number(digits: int) -> str:
    return str(random.randint(0, 10**digits - 1)).zfill(digits)

def print_client_data(client: Client) -> None:
    print("=" * 40)
    print(f"Client ID     : {client.client_id}")
    print(f"Name          : {client.client_name}")
    print(f"Account Number: {client.acc_number}")
    print(f"Agency Number : {client.agency_number}")
    print(f"Created On    : {client.creation_date}")
    print(f"Password      : {client.client_password}")
    print(f"Balance       : ${client.balance:,.2f}")
    print(f"Debt          : ${client.debt:,.2f}")
    print("=" * 40)


# Program Start
operators: List[Operator] = load_operators("operators.csv")
clients: List[Client] = load_clients("clients.csv")
transactions: List[Transaction] = load_transactions("transactions.csv")

while True:
    active_operator = Operator(
        operator_id=str(get_int("Enter operator ID: ")),
        operator_password=input("Enter operator password: "),
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

while True:
    control = input("What operation do you want to execute?:\n1-Access client data.\n2-Access operator data.\n3-log-off\n4-exit\n")
    match control:
        case "1":
            if active_operator.access_level >= 1:
                print("You will access client data")
                while True:
                    control = input("Which action to execute?:\n1-Register new client\n2-Remove client\n3-Log-in client\n4-Return to main menu\n5-Exit Application\n")
                    match control:
                        case "1":
                            # Create new client
                            new_client = Client(
                            client_id=input("Insert client ID: "),
                            client_name=input("Insert client's name: "),
                            acc_number="",
                            agency_number=input("Insert agency number: "),
                            creation_date=date.today(),
                            client_password=input("Insert client password: "),
                            balance=0.0,
                            debt=0.0
                            )

                            # Generate unique account number
                            while True:
                                temp_number = generate_random_number(8)
                                if check_acc_number_availability(clients, temp_number):
                                    new_client.acc_number = temp_number
                                    break
                        
                                clients.append(new_client)
                            print(f"New client registered:\n")
                            print_client_data(new_client)

                        case "2":

                        case "3":
                            search_value = input("Enter client ID or Account Number: ")
                            active_client = search_client(search_value, clients)
                            if active_client:
                                print(f"Client found: {active_client}")
                            else:
                                print("Client not found.")
            else:
                print("Access denied, call a superior")

        case "2":
            if active_operator.access_level >= 2:
                print("You will access operator data")
            else:
                print("Access denied, call a superior")

        case "3":
            print("Logging off...")
            break

        case "4":
            print("You will now exit")
            time.sleep(2)
            break

        case _:
            print("Invalid command, try again")

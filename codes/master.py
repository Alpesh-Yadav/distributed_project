from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
from threading import Lock
import os

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer): pass

accounts = {}
counter = {}
lock = Lock()

def initialize():
    print("Initializing master from master_data/...")
    if not os.path.exists("master_data"):
        os.makedirs("master_data")
    for filename in os.listdir("master_data"):
        if filename.startswith("data_") and filename.endswith(".txt"):
            acc = int(filename.split("_")[1].split(".")[0])
            with open(f"master_data/{filename}", "r") as f:
                lines = f.readlines()
                if lines:
                    last = lines[-1].split(":")
                    try:
                        accounts[acc] = float(last[1].split(";")[0])
                        counter[acc] = int(last[-1])
                    except:
                        accounts[acc] = 0.0
                        counter[acc] = 0

initialize()

def create_account(acc, initial_balance):
    with lock:
        if acc in accounts:
            return False
        accounts[acc] = initial_balance
        counter[acc] = 0
        with open(f"master_data/data_{acc}.txt", "w") as f:
            f.write(f"{acc}:{initial_balance};created;counter:0\n")
    return True

def deposit(acc, amount):
    with lock:
        if acc not in accounts:
            return False
        accounts[acc] += amount
        counter[acc] += 1
        with open(f"master_data/data_{acc}.txt", "a") as f:
            f.write(f"{acc}:{accounts[acc]};deposit:{amount};counter:{counter[acc]}\n")
    return accounts[acc]

def withdraw(acc, amount):
    with lock:
        if acc not in accounts:
            return "Account does not exist."
        if accounts[acc] < amount:
            return "Insufficient balance."
        accounts[acc] -= amount
        counter[acc] += 1
        with open(f"master_data/data_{acc}.txt", "a") as f:
            f.write(f"{acc}:{accounts[acc]};withdraw:{amount};counter:{counter[acc]}\n")
    return accounts[acc]

def transfer(from_acc, to_acc, amount):
    with lock:
        if from_acc not in accounts or to_acc not in accounts:
            return "One or both accounts do not exist."
        if accounts[from_acc] < amount:
            return "Insufficient balance."
        accounts[from_acc] -= amount
        counter[from_acc] += 1
        accounts[to_acc] += amount
        counter[to_acc] += 1
        with open(f"master_data/data_{from_acc}.txt", "a") as f:
            f.write(f"{from_acc}:{accounts[from_acc]};transfer_out:{amount};counter:{counter[from_acc]}\n")
        with open(f"master_data/data_{to_acc}.txt", "a") as f:
            f.write(f"{to_acc}:{accounts[to_acc]};transfer_in:{amount};counter:{counter[to_acc]}\n")
    return accounts[from_acc], accounts[to_acc]

def get_account_data(acc):
    with lock:
        if acc in accounts:
            return accounts[acc], counter[acc]
        return None, None

def get_statement(acc):
    try:
        with open(f"master_data/data_{acc}.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "No transaction history found."

server = ThreadedXMLRPCServer(("localhost", 8003), allow_none=True)
print("Master Server (M1) running on port 8003...")
server.register_function(create_account, "create_account")
server.register_function(deposit, "deposit")
server.register_function(withdraw, "withdraw")
server.register_function(transfer, "transfer")
server.register_function(get_account_data, "get_account_data")
server.register_function(get_statement, "get_statement")
server.serve_forever()

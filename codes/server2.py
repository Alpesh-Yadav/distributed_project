from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
from threading import Lock
import xmlrpc.client

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer): pass

master = xmlrpc.client.ServerProxy("http://localhost:8003/", allow_none=True)
accounts = {}
lock = Lock()

def account_exists(acc):
    bal, _ = master.get_account_data(acc)
    return bal is not None

def create_account(acc, initial_balance):
    if initial_balance < 0:
        return "Initial balance must be positive."
    with lock:
        if master.get_account_data(acc)[0] is not None:
            return "Account already exists."
        master.create_account(acc, initial_balance)
        accounts[acc] = {"balance": initial_balance, "history": [f"Account created with balance {initial_balance}"]}
    return f"Account {acc} created with balance ${initial_balance}"

def deposit(acc, amount):
    if amount < 0:
        return "Amount must be positive."
    with lock:
        new_bal = master.deposit(acc, amount)
        if new_bal is False:
            return "Account does not exist."
        accounts.setdefault(acc, {"balance": 0, "history": []})
        accounts[acc]["balance"] = new_bal
        accounts[acc]["history"].append(f"Deposited {amount}")
        return f"Deposit successful. New balance: ${new_bal}"

def withdraw(acc, amount):
    if amount < 0:
        return "Amount must be positive."
    with lock:
        result = master.withdraw(acc, amount)
        if isinstance(result, str):
            return result
        accounts.setdefault(acc, {"balance": 0, "history": []})
        accounts[acc]["balance"] = result
        accounts[acc]["history"].append(f"Withdrew {amount}")
        return f"Withdrawal successful. New balance: ${result}"

def transfer(from_acc, to_acc, amount):
    if amount < 0:
        return "Amount must be positive."
    with lock:
        result = master.transfer(from_acc, to_acc, amount)
        if isinstance(result, str):
            return result
        new_from, new_to = result
        accounts.setdefault(from_acc, {"balance": 0, "history": []})
        accounts.setdefault(to_acc, {"balance": 0, "history": []})
        accounts[from_acc]["balance"] = new_from
        accounts[to_acc]["balance"] = new_to
        accounts[from_acc]["history"].append(f"Transferred {amount} to {to_acc}")
        accounts[to_acc]["history"].append(f"Received {amount} from {from_acc}")
        return f"Transfer successful. New balance: ${new_from}"

def check_balance(acc):
    bal, _ = master.get_account_data(acc)
    return f"Balance: ${bal}" if bal is not None else "Account does not exist."

def statement(acc):
    return master.get_statement(acc)

server = ThreadedXMLRPCServer(("localhost", 8001), allow_none=True)  # 8001 for S2
print("Server running on port 8001...")
server.register_function(create_account, "create_account")
server.register_function(deposit, "deposit")
server.register_function(withdraw, "withdraw")
server.register_function(check_balance, "check_balance")
server.register_function(account_exists, "account_exists")
server.register_function(transfer, "transfer")
server.register_function(statement, "statement")
server.serve_forever()

from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import mysql.connector
import xmlrpc.client
from threading import Lock

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

master = xmlrpc.client.ServerProxy("http://localhost:8003/")
db = mysql.connector.connect(user='bankuser', password='Bankpass123!',
                             host='localhost', database='banking_system',
                             autocommit=False)
cursor = db.cursor(buffered=True)
lock = Lock()

def account_exists(acc):
    cursor.execute("SELECT 1 FROM accounts WHERE account_number = %s", (acc,))
    return cursor.fetchone() is not None

def create_account(acc, initial_balance):
    with lock:
        if account_exists(acc):
            return "Account already exists."
        cursor.execute("INSERT INTO accounts VALUES (%s, %s)", (acc, initial_balance))
        db.commit()
    return f"Account {acc} created with balance ${initial_balance}"

def count_transactions(acc):
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE account_number = %s", (acc,))
    return cursor.fetchone()[0]

def deposit(acc, amount):
    if amount < 0:
        return "Please enter a positive number."
    try:
        cursor.execute("START TRANSACTION")
        cursor.execute("SELECT balance FROM accounts WHERE account_number = %s FOR UPDATE", (acc,))
        result = cursor.fetchone()
        if not result:
            cursor.execute("ROLLBACK")
            return "Account does not exist."
        new_balance = result[0] + amount
        cursor.execute("UPDATE accounts SET balance = %s WHERE account_number = %s", (new_balance, acc))
        count = count_transactions(acc) + 1
        db.commit()
        master.deposit(acc, amount, new_balance, count)
        return f"Deposit successful. New balance: ${new_balance}"
    except Exception as e:
        db.rollback()
        return f"Error: {str(e)}"

def withdraw(acc, amount):
    if amount < 0:
        return "Please enter a positive number."
    try:
        cursor.execute("START TRANSACTION")
        cursor.execute("SELECT balance FROM accounts WHERE account_number = %s FOR UPDATE", (acc,))
        result = cursor.fetchone()
        if not result:
            cursor.execute("ROLLBACK")
            return "Account does not exist."
        balance = result[0]
        if balance < amount:
            cursor.execute("ROLLBACK")
            return "Insufficient balance."
        new_balance = balance - amount
        cursor.execute("UPDATE accounts SET balance = %s WHERE account_number = %s", (new_balance, acc))
        count = count_transactions(acc) + 1
        db.commit()
        master.withdraw(acc, amount, new_balance, count)
        return f"Withdrawal successful. New balance: ${new_balance}"
    except Exception as e:
        db.rollback()
        return f"Error: {str(e)}"

def check_balance(acc):
    cursor.execute("SELECT balance FROM accounts WHERE account_number = %s", (acc,))
    result = cursor.fetchone()
    if result:
        return f"Balance: ${result[0]}"
    return "Account does not exist."

def transfer(from_acc, to_acc, amount):
    if amount < 0:
        return "Please enter a positive number."
    try:
        cursor.execute("START TRANSACTION")
        cursor.execute("SELECT balance FROM accounts WHERE account_number = %s FOR UPDATE", (from_acc,))
        from_result = cursor.fetchone()
        cursor.execute("SELECT balance FROM accounts WHERE account_number = %s FOR UPDATE", (to_acc,))
        to_result = cursor.fetchone()
        if not from_result or not to_result:
            cursor.execute("ROLLBACK")
            return "One or both accounts do not exist."
        from_balance = from_result[0]
        to_balance = to_result[0]
        if from_balance < amount:
            cursor.execute("ROLLBACK")
            return "Insufficient balance."
        new_from = from_balance - amount
        new_to = to_balance + amount
        cursor.execute("UPDATE accounts SET balance = %s WHERE account_number = %s", (new_from, from_acc))
        cursor.execute("UPDATE accounts SET balance = %s WHERE account_number = %s", (new_to, to_acc))
        count_from = count_transactions(from_acc) + 1
        count_to = count_transactions(to_acc) + 1
        db.commit()
        master.transfer(from_acc, to_acc, amount, new_from, new_to, count_from, count_to)
        return f"Transfer successful. New balance: ${new_from}"
    except Exception as e:
        db.rollback()
        return f"Error: {str(e)}"

def statement(acc):
    cursor.execute("SELECT type, amount, balance_after, counter, timestamp FROM transactions WHERE account_number = %s", (acc,))
    records = cursor.fetchall()
    if not records:
        return "No transactions found."
    return "\n".join([f"{row[4]} | {row[0]} {row[1]} | Balance: {row[2]} | Txn#: {row[3]}" for row in records])

server = ThreadedXMLRPCServer(("localhost", 8000))
print("Server S1 running on port 8000 with MySQL")
server.register_function(create_account, "create_account")
server.register_function(account_exists, "account_exists")
server.register_function(deposit, "deposit")
server.register_function(withdraw, "withdraw")
server.register_function(check_balance, "check_balance")
server.register_function(transfer, "transfer")
server.register_function(statement, "statement")
server.serve_forever()

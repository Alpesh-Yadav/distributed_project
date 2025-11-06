from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import mysql.connector
from threading import Lock

lock = Lock()

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

db = mysql.connector.connect(user='bankuser', password='Bankpass123!',
                             host='localhost', database='banking_system')
cursor = db.cursor()

def log_transaction(account_number, type, amount, balance, counter):
    with lock:
        cursor.execute("""
            INSERT INTO transactions (account_number, type, amount, balance_after, counter)
            VALUES (%s, %s, %s, %s, %s)
        """, (account_number, type, amount, balance, counter))
        db.commit()
        return True

def deposit(acc, amount, new_balance, count):
    return log_transaction(acc, 'deposit', amount, new_balance, count)

def withdraw(acc, amount, new_balance, count):
    return log_transaction(acc, 'withdraw', amount, new_balance, count)

def transfer(from_acc, to_acc, amount, new_bal_from, new_bal_to, count_from, count_to):
    withdraw(from_acc, amount, new_bal_from, count_from)
    deposit(to_acc, amount, new_bal_to, count_to)
    return True

server = ThreadedXMLRPCServer(("localhost", 8003))
print("Master Server running on port 8003 with MySQL")
server.register_function(deposit, "deposit")
server.register_function(withdraw, "withdraw")
server.register_function(transfer, "transfer")
server.serve_forever()
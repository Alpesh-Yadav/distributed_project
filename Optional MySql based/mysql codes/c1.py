import xmlrpc.client

print("Select a Server to connect:")
print("1. Server S1")
print("2. Server S2")
choice = input("Enter 1 or 2: ")

if choice == "1":
    server = xmlrpc.client.ServerProxy("http://localhost:8000/", allow_none=True)
    print("Connected to Server S1")
elif choice == "2":
    server = xmlrpc.client.ServerProxy("http://localhost:8001/", allow_none=True)
    print("Connected to Server S2")
else:
    print("Invalid server choice.")
    exit()

def get_acc(prompt="Enter account number: "):
    try:
        acc = int(input(prompt))
        if acc <= 0:
            print("Account number must be positive.")
            return None
        return acc
    except:
        print("Invalid input.")
        return None

while True:
    print("\n0. Create New Account")
    print("1. Deposit")
    print("2. Withdraw")
    print("3. Transfer Money")
    print("4. Check Balance")
    print("5. View Statement")
    print("6. Exit")
    option = input("Choose an option (0–6): ")

    if option == "0":
        acc = get_acc("Enter new account number: ")
        if acc:
            if server.account_exists(acc):
                print("Account already exists.")
            else:
                try:
                    bal = float(input("Enter initial balance: "))
                    print(server.create_account(acc, bal))
                except:
                    print("Invalid amount.")

    elif option == "1":
        acc = get_acc()
        if acc and server.account_exists(acc):
            try:
                amt = float(input("Enter amount to deposit: "))
                print(server.deposit(acc, amt))
            except:
                print("Invalid amount.")
        else:
            print("Account does not exist.")

    elif option == "2":
        acc = get_acc()
        if acc and server.account_exists(acc):
            try:
                amt = float(input("Enter amount to withdraw: "))
                print(server.withdraw(acc, amt))
            except:
                print("Invalid amount.")
        else:
            print("Account does not exist.")

    elif option == "3":
        from_acc = get_acc("Transfer from account: ")
        to_acc = get_acc("Transfer to account: ")
        if from_acc and to_acc:
            try:
                amt = float(input("Enter amount to transfer: "))
                print(server.transfer(from_acc, to_acc, amt))
            except:
                print("Invalid amount.")

    elif option == "4":
        acc = get_acc()
        if acc:
            print(server.check_balance(acc))

    elif option == "5":
        acc = get_acc()
        if acc:
            print("Transaction History:\n" + server.statement(acc))

    elif option == "6":
        print("Exiting client...")
        break

    else:
        print("Invalid option.")

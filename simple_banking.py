# Write your code here
import random
import sqlite3


def luhn_15digit(str_of_numbers):
    numbers = []
    for i, n in enumerate(str_of_numbers):
        if i % 2:
            numbers.append(int(n))
        else:
            numbers.append(int(n) * 2 if int(n) * 2 < 10 else int(n) * 2 - 9)
    check_digit = 10 - sum(numbers) % 10 if sum(numbers) % 10 else 0
    return str(check_digit)


class BankAccount:
    MMI = '4'
    IIN = MMI + '00000'
    db_connection = sqlite3.connect('card.s3db')
    db_cursor = db_connection.cursor()
    db_cursor.execute('''CREATE TABLE IF NOT EXISTS card (
    id INTEGER,
    number TEXT,
    pin TEXT,
    balance INTEGER DEFAULT 0
    );'''.replace("  ", ''))
    db_connection.commit()
    db_cursor.execute("SELECT id FROM card")
    accounts = [i[0] for i in db_cursor.fetchall()]

    def __new__(cls, account=None):
        if account:
            if account in cls.accounts:
                return object.__new__(cls)
        else:
            return object.__new__(cls)

    def __init__(self, account=None):
        if account:
            account = self.db_get_account(account)
            self.account_id = account[0]
            self.card = account[1]
            self.pin = account[2]
            self.balance = account[3]
        else:
            self.account_id = self.create_account()
            self.card = self.create_card()
            self.pin = self.create_pin()
            self.balance = 0
            self.db_new_account()
            print(f'''
            Your card has been created
            Your card number:
            {self.card}
            Your card PIN:
            {self.pin}
            '''.replace("  ", ''))

    def create_account(self):
        account = random.randrange(10 ** 8, 10 ** 9)
        while account in self.accounts:
            account = random.randrange(10 ** 8, 10 ** 9)
        return account

    def create_card(self):
        checksum = luhn_15digit(self.IIN + str(self.account_id))
        return self.IIN + str(self.account_id) + checksum

    def create_pin(self):
        return str(random.randrange(10 ** 3, 10 ** 4))

    def db_new_account(self):
        self.db_cursor.execute("INSERT INTO card (id, number, pin) VALUES (?,?,?)",
                               (self.account_id, self.card, self.pin))
        self.db_connection.commit()
        BankAccount.accounts.append(self.account_id)

    def db_get_account(self, account):
        self.db_cursor.execute("SELECT * FROM card WHERE id=?", (account,))
        return self.db_cursor.fetchone()

    def db_update_balance(self):
        self.db_cursor.execute("UPDATE card SET balance=? WHERE id=?", (self.balance, self.account_id))
        self.db_connection.commit()

    def db_delete_account(self):
        self.db_cursor.execute("DELETE FROM card WHERE id=?", (self.account_id,))
        self.db_connection.commit()

    def add_income(self, amount_to_add):
        self.balance += amount_to_add
        self.db_update_balance()

    def transfer_funds_to(self, amount_to_transfer, recipient):
        self.balance -= amount_to_transfer
        self.db_update_balance()
        recipient_customer = BankAccount(recipient)
        recipient_customer.add_income(amount_to_transfer)

    def close_account(self):
        BankAccount.accounts.remove(self.account_id)
        self.db_delete_account()


exit_flag = False
while not exit_flag:
    user_input = input("1. Create an account\n2. Log into account\n0. Exit\n")
    if user_input == '0':
        exit_flag = True
    elif user_input == '1':
        new_account = BankAccount()
    elif user_input == '2':
        input_card = input("\nEnter your card number:\n")
        input_pin = input("Enter your PIN:\n")
        customer_account = int(input_card[6:15])
        customer = BankAccount(customer_account)
        if customer and customer.pin == input_pin:
            print("\nYou have successfully logged in!\n")
            while True:
                customer_input = input('''1. Balance
                2. Add income
                3. Do transfer
                4. Close account
                5. Log out
                0. Exit
                '''.replace("  ", ''))
                if customer_input == '0':
                    exit_flag = True
                    break
                elif customer_input == '1':
                    print("\nBalance:", customer.balance, '\n')
                elif customer_input == '2':
                    amount = int(input("\nEnter income:\n"))
                    customer.add_income(amount)
                    print("Income was added!\n")
                elif customer_input == '3':
                    receiver_card = input("\nTransfer\nEnter card number:\n")
                    receiver_account = int(receiver_card[6:-1])
                    if receiver_card == customer.card:
                        print("You can't transfer money to the same account!\n")
                    elif luhn_15digit(receiver_card[:-1]) != receiver_card[-1]:
                        print("Probably you made mistake in the card number. Please try again!\n")
                    elif receiver_account not in BankAccount.accounts:
                        print("Such a card does not exist.\n")
                    else:
                        amount = int(input("Enter how much money you want to transfer:\n"))
                        if amount > customer.balance:
                            print("Not enough money!\n")
                        else:
                            customer.transfer_funds_to(amount, receiver_account)
                            print("Success!\n")
                elif customer_input == '4':
                    customer.close_account()
                    print("\nThe account has been closed!\n")
                elif customer_input == '5':
                    print("\nYou have successfully logged out!\n")
                    break
        else:
            print("\nWrong card number or PIN!\n")
BankAccount.db_connection.close()
print("\nBye!")

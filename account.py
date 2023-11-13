import logging
import uuid
import hashlib
import json
import datetime
from typing import List, Tuple, Optional

logging.basicConfig(filename='bank.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

MIN_BALANCE = 10_000
FEE = 0.005

class BankAccount:
    
    account_number_counter = 0
    accounts = {}   # Stores all accounts 
    
    def __init__(self,name: str, balance=0, password="", card=None):
        """
        Initialize a new BankAccount object.

        Args:
            name (str): The name of the account holder.
            balance (float, optional): The initial account balance. Defaults to 0.
            password (str, optional): The password for the account. Defaults to ''.
        """
        
        self.name = name 
        self.balance = balance   
        self.account_number = str(uuid.uuid4())[:8] 
        self.password = self.set_password()    
        self.card = Card.generate_card(self.account_number)
        self.transaction_history = []
        BankAccount.accounts[self.card.card_number] = self


    def generate_account_number(self):
        BankAccount.account_number_counter += 1
        return f"ACC{BankAccount.account_number_counter:06d}"



    @property
    def balance(self) -> float:
        """Get the current account balance."""
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        """
        Set the current account balance.

        Args:
            value (float): The new account balance.
        """
        self._balance = value


    def set_password(self, password: str, password2) -> None:
        """
        Set the password for the account.

        Args:
            password (str): The new password for the account.
        """
        
        
        if password == password2:  
            password = password.encode()     
            hash_object = hashlib.sha256(password)
            hashed_password = hash_object.hexdigest()
        return hashed_password
    

    
    def deposit(self, amount: float) -> None:
        """
        Add funds to the account balance.

        Args:
            amount (float): The amount to deposit.
        """
        self.balance += amount
        self.transaction_history.append(("Deposit", amount))
        logging.info(f'Deposit of {amount} T to account {self.account_number}')


    def withdraw(self, amount: float) -> bool:
        """
        Subtract funds from the account balance.

        Args:
            amount (float): The amount to withdraw.

        Raises:
            ValueError: If the specified amount is greater than the account balance.

        Returns:
            bool: True if the withdrawal is successful, False otherwise.
        """
        if self.balance - amount < MIN_BALANCE:
            logging.warning(f'Attempted withdrawal of {amount} T from account {self.account_number} with insufficient funds')
            raise ValueError("Insufficient funds")
        else:
            self.balance -= amount + FEE
            self.transaction_history.append(("Withdrawal", amount))
            logging.info(f'Withdrawal of {amount} T from account {self.account_number}')
        return True


    def check_balance(func):
        """Decorator to check if account has enough balance before executing a transaction."""
        def wrapper(self, *args, **kwargs): 
       # Check if account has enough balance
            if self.balance < MIN_BALANCE:
             print("Insufficient funds")
            return None
         # Call original function
            return func(self, *args, **kwargs)
        return wrapper
    


    def transfer(self, amount: float, recipient: Optional['BankAccount'], password: str) -> None:
        """
        Transfer funds to another account.

        Args:
            self (BankAccount): The account sending the transfer.
            amount (float): The amount to transfer.
            recipient (Optional[BankAccount]): The account receiving the transfer, or None if the recipient doesn't exist.
            password (str): The password for the sender's account.

        Raises:
            ValueError: If the specified amount is greater than the account balance or
            if the password is incorrect.
        """
        if amount <= 0:
            raise ValueError("Invalid amount")
        if amount > self.balance:
            raise ValueError("Insufficient balance for transfer")
        if password != self.password:
            raise ValueError("Incorrect password for transfer")
        if recipient is not None:
            recipient.deposit(amount)
            self.balance -= amount
            self.balance -= self.calculate_fees(amount)
            self.transaction_history.append(('Transfer', amount, recipient.account_number))
            logging.info(f'Transfer of {amount} T from account {self.account_number} to account {recipient.account_number}')
        else:
            self.balance -= self.calculate_fees(amount)
            self.transaction_history.append(('Transfer', amount, "Non-existent account"))
            logging.info(f'Transfer of {amount} T from account {self.account_number} to non-existent account')
    

    
    def charge_wallet(card_number: str, cvv: str, password: str, amount: float) -> float:
        """
        Charge a wallet using the specified account's card details.

        Args:
            card_number (str): The card number associated with the account.
            cvv (str): The card security code.
            password (str): The account password.
            amount (float): The amount to charge the wallet.

            Returns:
            float: The amount successfully charged to the wallet.

        Raises:
            ValueError: If the specified credentials are invalid or if the account has insufficient funds.
        """
        if card_number not in BankAccount.accounts:
         raise ValueError("Invalid card details")
  
        account = BankAccount.accounts[card_number]
        try:
            transferred_amount = account.validate_transfer(amount, None, password, card_number, cvv)
        except ValueError as error:
            logging.error(str(error))
            raise ValueError(str(error))
  
        logging.info(f'Charge of {transferred_amount:.2f} T to wallet using account {account.account_number}')
  
        return transferred_amount
    

    def transfer_funds(card_number, cvv, password, amount, recipient):
        """
        Transfer funds from an account given card details and recipient.
        Args:
        card_number (str): The card number associated with the account
        cvv (str): The card security code 
        password (str): The account password   
        amount (float): The amount to transfer 
        recipient (BankAccount): The account to transfer funds to
    
        Returns:
        float: The amount actually transferred after fees  

        Raises:
        ValueError: If credentials are invalid or insufficient funds  
        """ 
        self = BankAccount(card_number)  
        if not self.authenticate(cvv, password):
            raise ValueError("Incorrect card details")  

        if amount > self.balance:
            raise ValueError("Insufficient funds")
     
        self.transfer(amount, recipient, password)

        transfer_amount = amount - self.calculate_fees(amount)  
        self.transaction_history.append(('Transfer', transfer_amount, recipient.account_number))  
        recipient.deposit(transfer_amount)     
    
        return transfer_amount


    def validate_transfer(self, amount: float, recipient: Optional['BankAccount'], password: str, card_number: str, cvv: str) -> float:
        """
        Validate a transfer of funds from the account.

        Args:
        amount (float): The amount to transfer.
        recipient (Optional[BankAccount]): The account to transfer the funds to, or None if the transfer is a charge.
        password (str): The password for the account.
        card_number (str): The card number associated with the account.
        cvv (str): The card security code.

        Returns:
         float: The amount successfully transferred.

        Raises:
         ValueError: If the specified amount is greater than the account balance or if the password is incorrect.
        """
        if amount <= 0:
            raise ValueError("Invalid amount")
        if password != self.password or card_number not in BankAccount.accounts:
         raise ValueError("Invalid credentials")
        if amount > self.balance:
         raise ValueError("Insufficient funds")
        if recipient is not None and recipient.account_number not in BankAccount.accounts:
         raise ValueError("Invalid recipient account number")

        self.balance -= amount
        if recipient is not None:
            recipient.balance += amount
            transferred_amount = amount
        else:
            transferred_amount = amount - self.calculate_fees(amount)

        return transferred_amount
    

    def get_transaction_history(self) -> List[Tuple[str, float]]:
        """
        Get the transaction history for the account.

        Returns:
            List[Tuple[str, float]]: A list of tuples representing 
            the transaction history, where each tuple contains the type
            of transaction ('Deposit', 'Withdrawal', or 'Transfer') 
            and the amount involved.
        """
        return self.transaction_history
    

    def get_balance(self):
         return self.balance
    

    def apply_fee(self, amount):
         self.balance -= amount


    def validate_password(self, password):
        password = password.encode()        
        hash_object = hashlib.sha256(password) 
        hashed_password = hash_object.hexdigest()        
        return hashed_password == self.password
    
    def save_accounts(self):
        """Save all accounts to a JSON file."""
        with open('accounts.json', 'w') as f:
            json.dump(BankAccount.accounts, f)
            logging.info('Accounts saved to file')


    def load_accounts(self):
        """Load account data from a JSON file."""
        with open('accounts.json') as f:
            data = json.load(f)
        BankAccount.accounts = data
        logging.info('Accounts loaded from file')
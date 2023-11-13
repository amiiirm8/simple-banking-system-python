
import hashlib
import logging
import json
import datetime
from typing import List, Tuple, Optional

from account import MIN_BALANCE

logging.basicConfig(filename='bank.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def check_balance(func):
    """Decorator to check if the account has enough balance before executing a transaction."""
    def wrapper(self, *args, **kwargs):
        # Check if the account has enough balance
        if self.balance < MIN_BALANCE:
            print("Insufficient funds")
            return None
        # Call the original function
        return func(self, *args, **kwargs)
    return wrapper

def validate_password(password, hashed_password):
    password = password.encode()
    hash_object = hashlib.sha256(password)
    return hash_object.hexdigest() == hashed_password

def save_accounts(accounts):
    """Save all accounts to a JSON file."""
    with open('accounts.json', 'w') as f:
        json.dump(accounts, f)
        logging.info('Accounts saved to file')

def load_accounts():
    """Load account data from a JSON file."""
    with open('accounts.json') as f:
        data = json.load(f)
    logging.info('Accounts loaded from file')
    return data

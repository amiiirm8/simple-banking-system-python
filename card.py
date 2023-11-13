
from ast import List
import logging
import random
import datetime
import json


class Card:         
        
   def __init__(self, card_number: str, cvv: int, exp_date: datetime.date) -> None:
        """
        Initialize a Card object.
        
        Args:
            card_number (str): The card number
            cvv (int): The CVV code
            exp_date (datetime.date): The card expiration date        
        """     
        """Generate a random card number, CVV and expiration date."""
        self.card_number = self.generate_card_number() 
        self.cvv = self.generate_cvv()
        self.exp_date = self.generate_exp_date()
        logging.info(f'New card generated: {self.card_number}')


   @staticmethod    
   def generate_number() -> str:
        """
        Generates a random 16-digit card number with a valid check digit.
        
        Returns:
        str: The generated card number.
        """
        digits = ["6", "1", "0", "4", "3", "3"] + random.sample(range(10), 9)
        check_digit = Card.calculate_check_digit(''.join(map(str, digits)))  
        card_number = ''.join(map(str, digits)) + str(check_digit)
        logging.info(f'Generated new card number: {card_number}')
        return card_number



   @staticmethod      
   def calculate_check_digit(number: str) -> int:
        """
        Calculates the check digit for a card number using the Luhn algorithm.
        
        Args:
        number (str): The card number to calculate the check digit for.
        
        Returns:
        int: The calculated check digit.
        """
        digits = list(map(int, reversed(number)))
        doubled_digits = [2 * digit if i % 2 == 1 else digit for i, digit in enumerate(digits)]
        subtracted_digits = [digit - 9 if digit > 9 else digit for digit in doubled_digits]
        total = sum(subtracted_digits)
        check_digit = (10 - (total % 10)) % 10
        return check_digit



   @staticmethod        
   def generate_cvv() -> int:
    """
       Generate a random 3-digit CVV.
       
       Returns:
           int: The generated CVV
    """
    cvv = random.randint(100, 999)
    logging.info(f'Generated new CVV: {cvv}')
    return cvv


   @staticmethod        
   def generate_exp_date() -> datetime.date:
        """Generate an expiration date 2 years from now."""
        exp_date = datetime.date.today() + datetime.timedelta(days=random.randint(365, 1825))
        logging.info(f'Generated new expiration date: {exp_date}')
        return exp_date


    
   def save(self)-> None:
        """Save the card data to a JSON file."""
        data = {
        "card_number": self.card_number,
        "cvv": self.cvv,
        "expiration": self.exp_date.isoformat()  
       }
       
        with open('cards.json', 'a') as f:
            json.dump(data, f)
        logging.info(f'Card data saved to file: {data}')

           
   @staticmethod
   def load_cards() -> List['Card']:
        """
        Load card data from a JSON file.

        Returns:
            List[Card]: A list of Card objects
        """
        cards = []
        with open('cards.json') as f:
            for line in f:
                data = json.loads(line)
                card = Card(data['card_number'], data['cvv'], datetime.date.fromisoformat(data['exp_date']))
                cards.append(card)
        logging.info(f'Loaded {len(cards)} cards from file')
        return cards
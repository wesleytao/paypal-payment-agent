from abc import ABC, abstractmethod
from typing import Dict, Optional, List

class PaymentProvider(ABC):
    """Base class for payment providers."""
    
    @abstractmethod
    def authenticate(self) -> Optional[str]:
        """
        Authenticate with the payment provider.
        
        Returns:
            Optional[str]: Authentication token if successful, None otherwise
        """
        pass
    
    @abstractmethod
    def send_money(self, recipient: str, amount: float, currency: str = "USD", note: str = None) -> Dict:
        """
        Send money to a recipient.
        
        Args:
            recipient: Email or ID of the recipient
            amount: Amount to send
            currency: Currency code (default: USD)
            note: Optional note for the transaction
            
        Returns:
            Dict containing the result of the operation
        """
        pass
    
    @abstractmethod
    def check_balance(self, currency: str = None) -> Dict:
        """
        Check account balance.
        
        Args:
            currency: Optional currency code to filter results
            
        Returns:
            Dict containing balance information
        """
        pass
    
    @abstractmethod
    def get_transactions(self, start_date: str = None, end_date: str = None) -> Dict:
        """
        Get transaction history.
        
        Args:
            start_date: Optional start date in ISO format
            end_date: Optional end date in ISO format
            
        Returns:
            Dict containing transaction history
        """
        pass

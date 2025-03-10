import time
import logging
import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta

from adapters.payment.base import PaymentProvider
from config.settings import PAYPAL_CONFIG

logger = logging.getLogger(__name__)

class PayPalAdapter(PaymentProvider):
    """PayPal payment provider implementation (using Sandbox mode only)."""
    
    def __init__(self):
        self.client_id = PAYPAL_CONFIG["client_id"]
        self.client_secret = PAYPAL_CONFIG["client_secret"]
        self.base_url = PAYPAL_CONFIG["base_url"]  # This is always sandbox URL per requirements
        
        logger.info(f"Initialized PayPal adapter with sandbox URL: {self.base_url}")
    
    def authenticate(self) -> Optional[str]:
        """Get PayPal OAuth access token from sandbox."""
        try:
            auth_url = f"{self.base_url}/v1/oauth2/token"
            headers = {
                "Accept": "application/json",
                "Accept-Language": "en_US"
            }
            data = {
                "grant_type": "client_credentials",
                "scope": "https://uri.paypal.com/services/payments/payment https://uri.paypal.com/services/payments/refund https://uri.paypal.com/services/reporting/search/read https://uri.paypal.com/services/wallet/balance/read"
            }
            
            logger.debug(f"Requesting OAuth token from {auth_url}")
            
            response = requests.post(
                auth_url,
                auth=(self.client_id, self.client_secret),
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                logger.info("Successfully obtained PayPal access token")
                return token
            else:
                logger.error(f"Failed to get access token: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            return None
    
    def send_money(self, recipient: str, amount: float, currency: str = "USD", note: str = None) -> Dict:
        """Send money via PayPal Payouts API (sandbox)."""
        access_token = self.authenticate()
        if not access_token:
            return {"status": "error", "message": "Failed to authenticate with PayPal"}
        
        url = f"{self.base_url}/v2/payments/payouts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Sending {amount} {currency} to {recipient}")
        
        payload = {
            "sender_batch_header": {
                "sender_batch_id": f"batch_{int(time.time())}",
                "email_subject": "You received a payment"
            },
            "items": [
                {
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": str(amount),
                        "currency": currency
                    },
                    "receiver": recipient,
                    "note": note or "Payment from PayPal Agent",
                    "sender_item_id": f"item_{int(time.time())}"
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code in (200, 201, 202):
                result = response.json()
                batch_id = result.get("batch_header", {}).get("payout_batch_id")
                logger.info(f"Payment successfully initiated, batch ID: {batch_id}")
                
                return {
                    "status": "success",
                    "payout_batch_id": batch_id,
                    "message": "Payment initiated successfully"
                }
            else:
                error_msg = f"PayPal API error: {response.text}"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg
                }
        except Exception as e:
            error_msg = f"Failed to send payment: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
    
    def check_balance(self, currency: str = None) -> Dict:
        """Check account balance using PayPal Reporting API (sandbox)."""
        access_token = self.authenticate()
        if not access_token:
            return {"status": "error", "message": "Failed to authenticate with PayPal"}
        
        url = f"{self.base_url}/v1/reporting/balances"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        params = {"currency_code": currency} if currency else {}
        
        logger.info(f"Checking balance with params: {params}")
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                balance_data = response.json()
                logger.info(f"Successfully retrieved balance information")
                
                return {
                    "status": "success",
                    "data": balance_data
                }
            else:
                error_msg = f"PayPal API error: {response.text}"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg
                }
        except Exception as e:
            error_msg = f"Failed to check balance: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
    
    def get_transactions(self, start_date: str = None, end_date: str = None) -> Dict:
        """Get transaction history using PayPal Reporting API (sandbox)."""
        access_token = self.authenticate()
        if not access_token:
            return {"status": "error", "message": "Failed to authenticate with PayPal"}
        
        # Default date range if not provided
        if not end_date:
            end_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S-0000")
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S-0000")
        
        url = f"{self.base_url}/v1/reporting/transactions"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        
        logger.info(f"Getting transactions from {start_date} to {end_date}")
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                transaction_data = response.json()
                logger.info(f"Successfully retrieved transaction history")
                
                return {
                    "status": "success",
                    "data": transaction_data
                }
            else:
                error_msg = f"PayPal API error: {response.text}"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg
                }
        except Exception as e:
            error_msg = f"Failed to get transactions: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }

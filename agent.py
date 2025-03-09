import os
import re
import json
import time
import random
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PayPalAgent:
    """
    A ReAct-based agent for processing natural language commands
    and executing PayPal API calls.
    """
    
    def __init__(self):
        """Initialize the PayPal Agent."""
        # Load environment variables if not already loaded
        load_dotenv()
        
        # Use environment variables if available
        self.client_id = os.getenv("PAYPAL_CLIENT_ID")
        self.client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
        self.mode = os.getenv("PAYPAL_MODE", "sandbox")
        
        # Set base URLs based on mode
        if self.mode == "sandbox":
            self.base_url = "https://api-m.sandbox.paypal.com"
        else:
            self.base_url = "https://api-m.paypal.com"
        
        # Check if credentials are available
        if self.client_id and self.client_secret:
            self.is_configured = True
        else:
            self.is_configured = False
            logger.warning("PayPal credentials not found. Please set credentials using set_credentials().")
        
        # For storing debug logs that will be displayed in the UI
        self.debug_logs = []  
        
    def debug_log(self, log_type, message, details=None):
        """Add a debug log that will be displayed in the UI.
        This method is meant to be connected to the app's add_debug_log function.
        
        Args:
            log_type (str): Type of log (info, error, action, reasoning)
            message (str): Log message
            details (dict, optional): Additional details
        """
        # Log to standard logger as well
        logger.info(f"{log_type}: {message} - {details}")
        
        # Store log for later retrieval by the app
        log_entry = {
            "timestamp": time.time(),
            "type": log_type,
            "message": message,
            "details": details
        }
        self.debug_logs.append(log_entry)
    def _get_access_token(self):
        """Get an OAuth access token from PayPal.
        
        Returns:
            str: The access token if successful, None otherwise.
        """
        try:
            auth_url = f"{self.base_url}/v1/oauth2/token"
            headers = {
                "Accept": "application/json",
                "Accept-Language": "en_US"
            }
            # Add specific scopes to request proper permissions
            data = {
                "grant_type": "client_credentials",
                "scope": "https://uri.paypal.com/services/payments/payment https://uri.paypal.com/services/payments/refund https://uri.paypal.com/services/reporting/search/read https://uri.paypal.com/services/wallet/balance/read"
            }
            
            response = requests.post(
                auth_url,
                auth=(self.client_id, self.client_secret),
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                return response.json()["access_token"]
            else:
                logger.error(f"Failed to get access token: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            return None            
    
    def set_credentials(self, client_id, client_secret, mode="sandbox"):
        """
        Set PayPal API credentials.
        
        Args:
            client_id (str): PayPal client ID.
            client_secret (str): PayPal client secret.
            mode (str, optional): PayPal mode ('sandbox' or 'live'). Defaults to "sandbox".
            
        Returns:
            bool: True if credentials were set successfully, False otherwise.
        """
        try:
            self.client_id = client_id
            self.client_secret = client_secret
            self.mode = mode
            
            # Update base URL based on mode
            if self.mode == "sandbox":
                self.base_url = "https://api-m.sandbox.paypal.com"
            else:
                self.base_url = "https://api-m.paypal.com"
            
            # Test the credentials by getting an access token
            access_token = self._get_access_token()
            if access_token:
                self.is_configured = True
                return True
            else:
                self.is_configured = False
                return False
        except Exception as e:
            logger.error(f"Failed to set PayPal credentials: {str(e)}")
            self.is_configured = False
            return False
            
    def set_credentials_with_debug(self, client_id, client_secret, mode="sandbox"):
        """
        Set PayPal API credentials with debug information.
        
        Args:
            client_id (str): PayPal client ID.
            client_secret (str): PayPal client secret.
            mode (str, optional): PayPal mode ('sandbox' or 'live'). Defaults to "sandbox".
            
        Returns:
            tuple: (success, debug_info) where success is a boolean and debug_info is a list of debug steps.
        """
        debug_info = []
        
        # Validate credentials
        debug_info.append({
            "type": "reasoning",
            "message": "Validating credentials",
            "details": {
                "client_id_length": len(client_id) if client_id else 0,
                "client_secret_length": len(client_secret) if client_secret else 0,
                "mode": mode
            }
        })
        
        if not client_id or not client_secret:
            debug_info.append({
                "type": "error",
                "message": "Missing credentials",
                "details": {
                    "client_id_provided": bool(client_id),
                    "client_secret_provided": bool(client_secret)
                }
            })
            return False, debug_info
        
        try:
            # Store credentials
            debug_info.append({
                "type": "action",
                "message": "Storing credentials",
                "details": {"mode": mode}
            })
            
            self.client_id = client_id
            self.client_secret = client_secret
            self.mode = mode
            
            # Set base URL based on mode
            if self.mode == "sandbox":
                self.base_url = "https://api-m.sandbox.paypal.com"
            else:
                self.base_url = "https://api-m.paypal.com"
                
            debug_info.append({
                "type": "api",
                "message": "Testing PayPal API connection",
                "details": {"base_url": self.base_url}
            })
            
            # Test credentials by getting an access token
            try:
                auth_url = f"{self.base_url}/v1/oauth2/token"
                headers = {
                    "Accept": "application/json",
                    "Accept-Language": "en_US"
                }
                data = {"grant_type": "client_credentials"}
                
                debug_info.append({
                    "type": "api",
                    "message": "Requesting OAuth token",
                    "details": {"url": auth_url}
                })
                
                response = requests.post(
                    auth_url,
                    auth=(self.client_id, self.client_secret),
                    headers=headers,
                    data=data
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.is_configured = True
                    
                    debug_info.append({
                        "type": "info",
                        "message": "PayPal API connection successful",
                        "details": {
                            "token_type": token_data.get("token_type"),
                            "expires_in": token_data.get("expires_in"),
                            "app_id": token_data.get("app_id")
                        }
                    })
                else:
                    self.is_configured = False
                    debug_info.append({
                        "type": "error",
                        "message": "Failed to authenticate with PayPal API",
                        "details": {
                            "status_code": response.status_code,
                            "response": response.text
                        }
                    })
                    return False, debug_info
            except Exception as e:
                self.is_configured = False
                debug_info.append({
                    "type": "error",
                    "message": "Error connecting to PayPal API",
                    "details": {"error": str(e)}
                })
                return False, debug_info
            
            return True, debug_info
        except Exception as e:
            debug_info.append({
                "type": "error",
                "message": "Error configuring PayPal SDK",
                "details": {"error": str(e)}
            })
            logger.error(f"Failed to set PayPal credentials: {str(e)}")
            return False, debug_info
    
    def process_message(self, message):
        """
        Process a natural language message and execute the appropriate PayPal action.
        
        Args:
            message (str): The user's natural language message.
            
        Returns:
            dict: Response containing the result of the action and any relevant information.
        """
        # Check if PayPal is configured
        if not self.is_configured:
            return {
                "type": "error",
                "message": "PayPal is not configured. Please set your PayPal credentials first."
            }
        
        # Step 1: Reasoning - Parse the message to determine intent and entities
        intent, entities = self._parse_message(message)
        
        if not intent:
            return {
                "type": "error",
                "message": "I couldn't understand what you want to do. Please try again with a clearer message."
            }
        
        # Step 2: Acting - Execute the appropriate action based on the intent
        return self._execute_action(intent, entities)
        
    def process_message_with_debug(self, message):
        """
        Process a natural language message with detailed debug information.
        
        Args:
            message (str): The user's natural language message.
            
        Returns:
            tuple: (response, debug_info) where response is a dict and debug_info is a list of debug steps.
        """
        # Clear previous debug logs
        self.debug_logs = []
        debug_info = []
        
        # Start timing
        start_time = time.time()
        
        # Check if PayPal is configured
        debug_info.append({
            "type": "reasoning",
            "message": "Checking if PayPal is configured",
            "details": {"is_configured": self.is_configured}
        })
        
        if not self.is_configured:
            debug_info.append({
                "type": "error",
                "message": "PayPal is not configured",
                "details": None
            })
            
            return {
                "type": "error",
                "message": "PayPal is not configured. Please set your PayPal credentials first."
            }, debug_info
        
        # Step 1: Reasoning - Parse the message to determine intent and entities
        debug_info.append({
            "type": "reasoning",
            "message": "Parsing message to determine intent",
            "details": {"message": message}
        })
        
        intent, entities = self._parse_message(message)
        
        # Log the parsing results
        if intent:
            debug_info.append({
                "type": "info",
                "message": f"Identified intent: {intent}",
                "details": {"entities": entities}
            })
        else:
            debug_info.append({
                "type": "error",
                "message": "Failed to identify intent",
                "details": {"message": message}
            })
            
            return {
                "type": "error",
                "message": "I couldn't understand what you want to do. Please try again with a clearer message."
            }, debug_info
        
        # Step 2: Acting - Determine which action to execute
        debug_info.append({
            "type": "action",
            "message": f"Preparing to execute action for intent: {intent}",
            "details": None
        })
        
        # Step 3: Execute the action and get the result
        try:
            result = self._execute_action(intent, entities)
            
            # Log the execution result
            debug_info.append({
                "type": "info",
                "message": f"Action executed: {intent}",
                "details": {"result_type": result.get("type")}
            })
            
            # Calculate processing time
            processing_time = time.time() - start_time
            debug_info.append({
                "type": "info",
                "message": "Processing completed",
                "details": {"processing_time_ms": round(processing_time * 1000)}
            })
            
            # Include any debug logs collected during processing
            if self.debug_logs:
                debug_info.extend(self.debug_logs)
            
            return result, debug_info
        except Exception as e:
            debug_info.append({
                "type": "error",
                "message": f"Error executing action: {intent}",
                "details": {"error": str(e)}
            })
            
            # Include any debug logs collected during processing
            if self.debug_logs:
                debug_info.extend(self.debug_logs)
            
            return {
                "type": "error",
                "message": f"An error occurred while executing {intent}: {str(e)}"
            }, debug_info
    
    def _parse_message(self, message):
        """
        Parse the user's message to determine intent and extract entities.
        
        Args:
            message (str): The user's natural language message.
            
        Returns:
            tuple: (intent, entities) where intent is a string and entities is a dictionary.
        """
        # Convert message to lowercase for easier processing
        message = message.lower()
        
        # Define patterns for different intents
        send_money_patterns = [
            r"send\s+(\$?[\d.]+)\s+to\s+([a-zA-Z\s]+)",
            r"pay\s+([a-zA-Z\s]+)\s+(\$?[\d.]+)",
            r"transfer\s+(\$?[\d.]+)\s+to\s+([a-zA-Z\s]+)",
            r"send\s+([a-zA-Z\s]+)\s+(\$?[\d.]+)",
            r"give\s+([a-zA-Z\s]+)\s+(\$?[\d.]+)"
        ]
        
        check_balance_patterns = [
            r"(check|show|what('s| is))\s+my\s+balance",
            r"how\s+much\s+(money|cash|funds)\s+(do\s+i\s+have|is\s+in\s+my\s+account)"
        ]
        
        transaction_history_patterns = [
            r"(show|get|list)\s+(my\s+)?(recent\s+)?(transactions|payments|history)",
            r"what\s+(are\s+my|have\s+been\s+my)\s+(recent\s+)?(transactions|payments)"
        ]
        
        # Check for send money intent
        for pattern in send_money_patterns:
            match = re.search(pattern, message)
            if match:
                groups = match.groups()
                
                # Determine which group is the amount and which is the recipient
                if groups[0].replace('$', '').replace('.', '').isdigit():
                    amount = groups[0].replace('$', '')
                    recipient = groups[1].strip()
                else:
                    amount = groups[1].replace('$', '')
                    recipient = groups[0].strip()
                
                return "send_money", {"recipient": recipient, "amount": amount}
        
        # Check for check balance intent
        for pattern in check_balance_patterns:
            if re.search(pattern, message):
                return "check_balance", {}
        
        # Check for transaction history intent
        for pattern in transaction_history_patterns:
            if re.search(pattern, message):
                return "transaction_history", {}
        
        # If no intent is matched, return None
        return None, {}
    
    def _execute_action(self, intent, entities):
        """
        Execute the appropriate action based on the intent and entities.
        
        Args:
            intent (str): The user's intent.
            entities (dict): Entities extracted from the user's message.
            
        Returns:
            dict: Response containing the result of the action.
        """
        try:
            if intent == "send_money":
                return self._send_money(entities.get("recipient"), entities.get("amount"))
            elif intent == "check_balance":
                return self._check_balance()
            elif intent == "transaction_history":
                return self._get_transaction_history()
            else:
                return {
                    "type": "error",
                    "message": f"I don't know how to {intent} yet."
                }
        except Exception as e:
            logger.error(f"Error executing action {intent}: {str(e)}")
            return {
                "type": "error",
                "message": f"An error occurred while executing {intent}: {str(e)}"
            }
    
    def _send_money(self, recipient, amount):
        """
        Send money to a recipient using the PayPal REST API.
        
        Args:
            recipient (str): Email or PayPal ID of the recipient.
            amount (str): Amount to send.
            
        Returns:
            dict: Response containing the status of the transaction.
        """
        try:
            # Convert amount to float
            amount_float = float(amount)
            
            # Get access token
            access_token = self._get_access_token()
            if not access_token:
                return {
                    "type": "error",
                    "message": "Failed to authenticate with PayPal API"
                }
            
            # Create a payout using the Payouts API
            logger.info(f"Sending ${amount_float} to {recipient} using PayPal API")
            
            # Set up API request
            payouts_url = f"{self.base_url}/v1/payments/payouts"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Create a unique batch ID
            batch_id = f"BATCH-{int(time.time())}-{random.randint(1000, 9999)}"
            
            # Prepare the payout data
            payload = {
                "sender_batch_header": {
                    "sender_batch_id": batch_id,
                    "email_subject": "You received a payment",
                    "email_message": "You received a payment. Thanks for using our service!"
                },
                "items": [
                    {
                        "recipient_type": "EMAIL",
                        "amount": {
                            "value": str(amount_float),
                            "currency": "USD"
                        },
                        "note": "Thanks for your patronage!",
                        "receiver": recipient,
                        "sender_item_id": f"ITEM-{int(time.time())}"
                    }
                ]
            }
            
            # Make the API request
            payout_response = requests.post(payouts_url, headers=headers, json=payload)
            logger.info(f"Payout API status code: {payout_response.status_code}")
            
            if payout_response.status_code in [200, 201, 202]:
                payout_data = payout_response.json()
                batch_id = payout_data.get("batch_header", {}).get("payout_batch_id", "")
                batch_status = payout_data.get("batch_header", {}).get("batch_status", "")
                
                return {
                    "type": "success",
                    "message": f"Successfully sent ${amount_float} to {recipient}",
                    "details": {
                        "payout_batch_id": batch_id,
                        "status": batch_status
                    }
                }
            else:
                error_message = payout_response.json().get("message", "Unknown error")
                logger.error(f"Failed to send money: {payout_response.text}")
                return {
                    "type": "error",
                    "message": f"Failed to send money: {error_message}"
                }
        except Exception as e:
            logger.error(f"Error sending money: {str(e)}")
            return {
                "type": "error",
                "message": f"An error occurred while sending money: {str(e)}"
            }
    
    def _check_balance(self):
        """
        Check the user's PayPal balance using the PayPal REST API.
        
        Returns:
            dict: Response containing the user's balance or an error message.
        """
        try:
            # Get access token
            access_token = self._get_access_token()
            if not access_token:
                return {
                    "type": "error",
                    "message": "Failed to authenticate with PayPal API"
                }
            
            # Use the v1 reporting endpoint
            logger.info("Fetching balance using PayPal v1 Reporting API")
            today = datetime.now().strftime("%Y-%m-%d")
            
            reporting_url = f"{self.base_url}/v1/reporting/balances"
            params = {
                "currency_code": "USD",
                "as_of_date": today
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Log the API request details
            self.debug_log("info", "Making PayPal API request", {
                "url": reporting_url,
                "parameters": params,
                "api_version": "v1 Reporting"
            })
            
            # Print API request details to terminal
            print("\n===== PAYPAL API REQUEST =====")
            print(f"URL: {reporting_url}")
            print(f"Parameters: {params}")
            print(f"Headers: {headers}")
            print("==============================\n")
            
            # Make the API request
            reporting_response = requests.get(reporting_url, headers=headers, params=params)
            self.debug_log("info", "PayPal API response received", {
                "status_code": reporting_response.status_code,
                "api_version": "v1 Reporting"
            })
            
            # Print API response details to terminal
            print("\n===== PAYPAL API RESPONSE =====")
            print(f"Status Code: {reporting_response.status_code}")
            print(f"Response Headers: {dict(reporting_response.headers)}")
            print("Response Body:")
            
            if reporting_response.status_code == 200:
                reporting_data = reporting_response.json()
                print(json.dumps(reporting_data, indent=2))
                print("==============================\n")
                
                # Log the full API response
                self.debug_log("info", "PayPal balance data retrieved", {
                    "response_data": reporting_data,
                    "api_version": "v1 Reporting"
                })
                # Extract balance from the correct path in the API response
                balances = reporting_data.get("balances", [])
                if balances and len(balances) > 0:
                    first_balance = balances[0]
                    available_balance = first_balance.get("available_balance", {}).get("value", "0.00")
                    currency = first_balance.get("available_balance", {}).get("currency_code", "USD")
                else:
                    available_balance = "0.00"
                    currency = "USD"
                
                # Log the specific balance value from the API
                self.debug_log("info", "Balance value extracted from API", {
                    "balance": available_balance,
                    "currency": currency,
                    "source": "PayPal REST API v1 Reporting",
                    "balance_path": "balances[0].available_balance.value"
                })
                
                formatted_amount = "{:,.2f}".format(float(available_balance))
                
                return {
                    "type": "success",
                    "message": f"Your current balance is ${formatted_amount}",
                    "details": {
                        "balance": float(available_balance),
                        "currency": currency,
                        "source": "PayPal REST API v1 Reporting"
                    }
                }
            else:
                logger.error(f"V1 API failed: {reporting_response.text}")
                return {
                    "type": "error",
                    "message": "Unable to retrieve your PayPal balance. This may be due to API permission restrictions."
                }
        except Exception as e:
            logger.error(f"Error checking balance: {str(e)}")
            return {
                "type": "error",
                "message": f"An error occurred while checking your balance: {str(e)}"
            }
    
    def _get_transaction_history(self):
        """
        Get the user's transaction history using the PayPal REST API.
        
        Returns:
            dict: Response containing the user's transaction history.
        """
        try:
            # Get access token
            access_token = self._get_access_token()
            if not access_token:
                return {
                    "type": "error",
                    "message": "Failed to authenticate with PayPal API"
                }
            
            # Use the transactions search endpoint
            logger.info("Fetching transaction history using PayPal API")
            
            # Set up date range (last 30 days)
            end_date = datetime.now()
            start_date = end_date - datetime.timedelta(days=30)
            
            # Format dates for API
            start_date_str = start_date.strftime("%Y-%m-%dT00:00:00Z")
            end_date_str = end_date.strftime("%Y-%m-%dT23:59:59Z")
            
            # Set up API request
            transactions_url = f"{self.base_url}/v1/reporting/transactions"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            params = {
                "start_date": start_date_str,
                "end_date": end_date_str,
                "fields": "transaction_info,payer_info,shipping_info,auction_info,cart_info,incentive_info,store_info"
            }
            
            # Make the API request
            transactions_response = requests.get(transactions_url, headers=headers, params=params)
            logger.info(f"Transactions API status code: {transactions_response.status_code}")
            
            if transactions_response.status_code == 200:
                transactions_data = transactions_response.json()
                logger.info(f"Found {len(transactions_data.get('transaction_details', []))} transactions")
                
                # Process and format the transactions
                transactions = []
                for transaction in transactions_data.get("transaction_details", []):
                    transaction_info = transaction.get("transaction_info", {})
                    
                    # Extract relevant information
                    transactions.append({
                        "id": transaction_info.get("transaction_id", ""),
                        "date": transaction_info.get("transaction_initiation_date", ""),
                        "amount": float(transaction_info.get("transaction_amount", {}).get("value", 0)),
                        "description": transaction_info.get("transaction_note", "Transaction"),
                        "status": transaction_info.get("transaction_status", "")
                    })
                
                return {
                    "type": "success",
                    "message": "Here are your recent transactions:",
                    "details": {
                        "transactions": transactions
                    }
                }
            else:
                logger.error(f"Failed to get transactions: {transactions_response.text}")
                return {
                    "type": "error",
                    "message": "Unable to retrieve your transaction history. This may be due to API permission restrictions."
                }
        except Exception as e:
            logger.error(f"Error getting transaction history: {str(e)}")
            return {
                "type": "error",
                "message": f"An error occurred while getting your transaction history: {str(e)}"
            }

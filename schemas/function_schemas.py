# Function schemas for OpenAI function calling

# Schema for sending money
SEND_MONEY_SCHEMA = {
    "name": "send_money",
    "description": "Send money to a recipient using PayPal (sandbox mode)",
    "parameters": {
        "type": "object",
        "properties": {
            "recipient": {
                "type": "string",
                "description": "Recipient's PayPal email address"
            },
            "amount": {
                "type": "number",
                "description": "Amount to send"
            },
            "currency": {
                "type": "string",
                "description": "Currency code (e.g., USD)",
                "default": "USD"
            },
            "note": {
                "type": "string",
                "description": "Optional note to include with the payment"
            }
        },
        "required": ["recipient", "amount"]
    }
}

# Schema for checking balance
CHECK_BALANCE_SCHEMA = {
    "name": "check_balance",
    "description": "Check PayPal account balance (sandbox mode)",
    "parameters": {
        "type": "object",
        "properties": {
            "currency": {
                "type": "string",
                "description": "Currency code to filter results (e.g., USD)",
                "default": "USD"
            }
        }
    }
}

# Schema for getting transaction history
GET_TRANSACTIONS_SCHEMA = {
    "name": "get_transactions",
    "description": "Get transaction history from PayPal (sandbox mode)",
    "parameters": {
        "type": "object",
        "properties": {
            "start_date": {
                "type": "string",
                "description": "Start date in ISO format (e.g., 2023-01-01T00:00:00-0000)"
            },
            "end_date": {
                "type": "string",
                "description": "End date in ISO format (e.g., 2023-01-31T23:59:59-0000)"
            }
        }
    }
}

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify

from adapters.llm.openai import OpenAIAdapter
from adapters.payment.paypal import PayPalAdapter
from functions.registry import FunctionRegistry
from core.agent import PayPalReactAgent
from schemas.function_schemas import (
    SEND_MONEY_SCHEMA,
    CHECK_BALANCE_SCHEMA,
    GET_TRANSACTIONS_SCHEMA
)
from utils.logging import setup_logging

# Setup logging
logger = setup_logging()

app = Flask(__name__)

# Create an instance of the PayPal agent
def create_agent():
    """Create and configure the PayPal agent."""
    # Initialize adapters
    llm = OpenAIAdapter()
    payment = PayPalAdapter()  # Always uses sandbox mode
    
    # Initialize function registry
    functions = FunctionRegistry()
    
    # Register payment functions
    functions.register(
        "send_money",
        payment.send_money,
        SEND_MONEY_SCHEMA
    )
    
    functions.register(
        "check_balance",
        payment.check_balance,
        CHECK_BALANCE_SCHEMA
    )
    
    functions.register(
        "get_transactions",
        payment.get_transactions,
        GET_TRANSACTIONS_SCHEMA
    )
    
    # Create agent
    return PayPalReactAgent(llm, payment, functions)

# Create a global agent instance
paypal_agent = create_agent()

@app.route('/')
def home():
    """Render the home page."""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat API endpoint."""
    data = request.json
    user_message = data.get('message', '')
    
    # DEBUG logs for terminal only
    logger.debug(f"Received chat message details: {user_message}")
    # INFO logs for both terminal and UI
    logger.info(f"Received chat message")
    
    try:
        # Process the message with the PayPal agent
        agent_response = paypal_agent.process_message(user_message)
        
        logger.info(f"Agent response: {agent_response}")
        
        # With our simplified adapter, we don't have function calling,
        # so we'll just return the response as text
        response_type = "text"
        response_details = None
        
        # Check if we have an error response
        if agent_response.get("status") == "error":
            return jsonify({
                "status": "error",
                "error": agent_response.get("message", "Unknown error")
            })
        
        # If user asks about balance, do a manual check
        if "balance" in user_message.lower() or "how much" in user_message.lower():
            logger.info("Balance request detected, manually querying PayPal")
            try:
                # Manually call PayPal adapter
                payment_adapter = PayPalAdapter()
                balance_result = payment_adapter.check_balance()
                if balance_result.get("status") == "success":
                    response_type = "balance"
                    response_details = {"balance": balance_result.get("data", {})}
            except Exception as balance_error:
                logger.error(f"Error checking balance: {str(balance_error)}")
        
        # If user asks about transactions, do a manual check
        if "transactions" in user_message.lower() or "history" in user_message.lower():
            logger.info("Transaction history request detected, manually querying PayPal")
            try:
                # Manually call PayPal adapter
                payment_adapter = PayPalAdapter()
                tx_result = payment_adapter.get_transactions()
                if tx_result.get("status") == "success":
                    response_type = "transaction_history"
                    response_details = {"transactions": tx_result.get("data", [])}
            except Exception as tx_error:
                logger.error(f"Error getting transactions: {str(tx_error)}")
        
        # Extract the response message from agent response
        response_message = agent_response.get("response", "")
        
        # If no response (which shouldn't happen), provide a fallback
        if not response_message:
            response_message = "I'm your PayPal assistant. How can I help you today?"
            
        return jsonify({
            "status": "success",
            "response": {
                "message": response_message,
                "type": response_type,
                "details": response_details,
                "agent_logs": agent_response.get("user_logs", [])  # Include user-facing logs
            }
        })
    
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        })

@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    """Handle PayPal authentication."""
    data = request.json
    client_id = data.get('client_id', '')
    client_secret = data.get('client_secret', '')
    
    logger.info(f"Authentication attempt with client ID: {client_id}")
    
    try:
        # In a real application, you would validate these credentials
        # For this demo, we'll just check if they're not empty
        if client_id and client_secret:
            # Here you would actually authenticate with PayPal
            # Since we're in sandbox mode, we'll just simulate a successful auth
            
            return jsonify({
                "status": "success",
                "message": "Authentication successful"
            })
        else:
            return jsonify({
                "status": "error",
                "error": "Invalid credentials"
            })
    
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        })

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """Reset the conversation history."""
    try:
        # Reset the agent's conversation history
        paypal_agent.conversation.clear()
        
        logger.info("[SANDBOX] Conversation history has been reset")
        
        return jsonify({
            "status": "success",
            "message": "Conversation has been reset"
        })
    
    except Exception as e:
        logger.error(f"Error resetting conversation: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        })

if __name__ == '__main__':
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='PayPal Payment Agent Web App')
    parser.add_argument('--port', type=int, default=5001, help='Port to run the web app on')
    args = parser.parse_args()
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=args.port)

# PayPal Merchant Assistant

A conversational agent that uses the ReAct framework to process natural language payment instructions and execute them through the PayPal API.

## User Interface

### Main Chat Interface
![PayPal Merchant Assistant UI](images/UI1.png)

*The PayPal Merchant Assistant provides a chat interface for managing PayPal transactions and checking account information using the PayPal REST API in sandbox mode.*

### Debug Information Panel
![PayPal Merchant Assistant Debug Panel](images/UI2.png)

*The debug panel shows detailed information about API calls, including endpoints, parameters, and responses.*

## Features

- **Natural Language Processing**: Understand and process user commands like "send $20 to Alex" or "check my balance"
- **Autonomous API Selection**: The agent automatically decides which PayPal API to call based on the user's input
- **Chat Interface**: User-friendly chat interface for interacting with the agent
- **Core PayPal Operations**: Support for sending money, checking balance, and viewing transaction history

## Requirements

- Python 3.7+
- Flask 2.2.3
- PayPal SDK 1.13.1
- Other dependencies listed in requirements.txt

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your PayPal API credentials:
   ```
   PAYPAL_CLIENT_ID=your_client_id_here
   PAYPAL_CLIENT_SECRET=your_client_secret_here
   PAYPAL_MODE=sandbox  # Use 'live' for production
   ```
4. Run the application:
   ```
   python app.py
   ```
5. Open your browser and navigate to `http://127.0.0.1:5000`

## Usage

1. Type natural language commands in the chat window:
   - "Send $50 to john@example.com"
   - "Check my balance"
   - "Show my recent transactions"

2. The agent will process your command, execute the appropriate PayPal API call, and respond with the result.

## How It Works

The agent uses a ReAct (Reasoning + Acting) framework:

1. **Reasoning**: Parses user input to understand intent and extract entities
2. **Acting**: Translates the parsed information into PayPal API calls
3. **Feedback**: Provides feedback to the user on the success or failure of their request

## Security Note

This application handles sensitive financial information. In a production environment, additional security measures would be needed:
- Secure user authentication
- API request validation
- Rate limiting
- Input sanitization
- Secure credential storage

## Development

To extend this agent:
1. Add new intent patterns in the `_parse_message` method
2. Create corresponding action methods
3. Update the `_execute_action` method to call the new actions

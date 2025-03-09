import os
import json
import time
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from agent import PayPalAgent

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize PayPal Agent
paypal_agent = PayPalAgent()

# Connect the agent's debug_log method to our add_debug_log function
def agent_debug_log_handler(log_type, message, details=None):
    add_debug_log(log_type, message, details)
    
# Override the agent's debug_log method
paypal_agent.debug_log = agent_debug_log_handler

# Store debug logs in memory
debug_logs = []

def add_debug_log(log_type, message, details=None):
    """Add a debug log entry."""
    log_entry = {
        "timestamp": time.time(),
        "type": log_type,
        "message": message,
        "details": details
    }
    debug_logs.append(log_entry)
    # Keep only the last 100 logs to avoid memory bloat
    if len(debug_logs) > 100:
        debug_logs.pop(0)
    return log_entry

@app.route('/')
def index():
    """Render the chat interface."""
    # Log page load
    add_debug_log("info", "Main page loaded", {"user_agent": request.headers.get('User-Agent')})
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process user message and return agent response."""
    try:
        start_time = time.time()
        data = request.json
        user_message = data.get('message', '')
        
        add_debug_log("info", "Chat request received", {"message": user_message})
        
        if not user_message:
            add_debug_log("error", "No message provided in request")
            return jsonify({
                "status": "error",
                "error": "No message provided"
            }), 400
        
        # Log reasoning process start
        add_debug_log("reasoning", "Starting message parsing", {"input": user_message})
        
        # Process the message using the PayPal Agent
        response, debug_info = paypal_agent.process_message_with_debug(user_message)
        
        # Log each step of the debug info
        for debug_step in debug_info:
            add_debug_log(
                debug_step.get("type", "info"),
                debug_step.get("message", ""),
                debug_step.get("details", None)
            )
        
        # Calculate response time
        processing_time = time.time() - start_time
        add_debug_log("info", "Request processed", {"processing_time_ms": round(processing_time * 1000)})
        
        # Return response with debug logs
        return jsonify({
            "status": "success",
            "response": response,
            "debug_logs": debug_logs[-10:]  # Send the 10 most recent logs
        })
    except Exception as e:
        add_debug_log("error", "Error processing chat request", {"error": str(e)})
        return jsonify({
            "status": "error",
            "error": str(e),
            "debug_logs": debug_logs[-10:]
        }), 500

@app.route('/api/debug/logs', methods=['GET'])
def get_debug_logs():
    """Get debug logs."""
    count = request.args.get('count', 10, type=int)
    return jsonify({
        "status": "success",
        "logs": debug_logs[-count:]
    })

@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    """Authenticate with PayPal."""
    try:
        start_time = time.time()
        data = request.json
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        
        add_debug_log("info", "Authentication attempt", {"client_id_provided": bool(client_id)})
        
        if not client_id or not client_secret:
            add_debug_log("error", "Missing credentials", {"client_id_provided": bool(client_id), "client_secret_provided": bool(client_secret)})
            return jsonify({
                "status": "error",
                "error": "Client ID and Client Secret are required"
            }), 400
        
        # Log authentication start
        add_debug_log("api", "Setting PayPal credentials")
        
        # Set the credentials in the PayPal Agent
        success, auth_debug_info = paypal_agent.set_credentials_with_debug(client_id, client_secret)
        
        # Log each step of the debug info
        for debug_step in auth_debug_info:
            add_debug_log(
                debug_step.get("type", "info"),
                debug_step.get("message", ""),
                debug_step.get("details", None)
            )
        
        # Calculate response time
        processing_time = time.time() - start_time
        
        if success:
            add_debug_log("action", "Authentication successful", {"processing_time_ms": round(processing_time * 1000)})
            return jsonify({
                "status": "success",
                "message": "Authentication successful",
                "debug_logs": debug_logs[-10:]
            })
        else:
            add_debug_log("error", "Authentication failed", {"processing_time_ms": round(processing_time * 1000)})
            return jsonify({
                "status": "error",
                "error": "Failed to authenticate with PayPal",
                "debug_logs": debug_logs[-10:]
            }), 401
    except Exception as e:
        add_debug_log("error", "Error during authentication", {"error": str(e)})
        return jsonify({
            "status": "error",
            "error": str(e),
            "debug_logs": debug_logs[-10:]
        }), 500

if __name__ == '__main__':
    add_debug_log("info", "Application started", {"mode": os.getenv("PAYPAL_MODE", "sandbox")})
    app.run(debug=True, port=5001)

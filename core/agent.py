import json
import logging
from typing import Dict, List, Any, Optional

from core.conversation import ConversationManager
from adapters.llm.base import LLMProvider
from adapters.payment.base import PaymentProvider
from functions.registry import FunctionRegistry

logger = logging.getLogger(__name__)

class PayPalReactAgent:
    """
    Core agent that orchestrates LLM, payment provider, and function execution.
    """
    
    def __init__(
        self, 
        llm_provider: LLMProvider,
        payment_provider: PaymentProvider,
        function_registry: FunctionRegistry,
        max_conversation_history: int = 100
    ):
        """
        Initialize the PayPal ReAct Agent.
        
        Args:
            llm_provider: LLM provider for natural language processing
            payment_provider: Payment provider for executing payment actions
            function_registry: Registry of available functions
            max_conversation_history: Maximum number of messages to keep in history
        """
        self.llm = llm_provider
        self.payment = payment_provider
        self.functions = function_registry
        self.conversation = ConversationManager(max_history=max_conversation_history)
        
        logger.info("PayPal ReAct Agent initialized")
    
    def process_message(self, user_message: str) -> Dict:
        """
        Process a user message with the ReAct pattern (reasoning and acting).
        
        This implementation follows the ReAct pattern where the LLM can:
        1. Reason about the user's request
        2. Decide to call a PayPal API function (in sandbox mode only)
        3. Receive the function result
        4. Reason about the result and potentially call another function
        5. Provide a final response based on all interactions
        
        Args:
            user_message: Natural language message from the user
            
        Returns:
            Dict containing the response and logs of all sandbox operations
        """
        # Add user message to conversation
        self.conversation.add_message("user", user_message)
        
        # Use DEBUG for terminal-only detailed logs
        logger.debug(f"Processing user message details: {user_message}")
        
        # Use INFO for user-visible logs (both terminal and UI)
        logger.info(f"Processing user request")
        
        # Track user-visible activities
        user_logs = []
        user_logs.append("[SANDBOX] Processing request with PayPal REST API (sandbox mode only)")
        
        # Get available functions from registry
        available_functions = self.functions.get_all_functions()
        
        # Initialize response and turn counter
        max_turns = 3  # Limit the number of function calls per request
        turns = 0
        
        try:
            # Get initial LLM completion with function calling
            logger.debug(f"[SANDBOX] Sending initial request to LLM with {len(available_functions)} available functions")
            current_response = self.llm.get_completion(
                messages=self.conversation.get_messages(),
                functions=available_functions
            )
            
            # Process function calls in a loop
            while turns < max_turns and "function_call" in current_response:
                turns += 1
                
                # Extract function details
                function_name = current_response["function_call"]["name"]
                arguments_str = current_response["function_call"]["arguments"]
                arguments = json.loads(arguments_str)
                
                # Log function execution (sandbox mode only)
                logger.info(f"[SANDBOX] Executing PayPal function: {function_name}")
                logger.debug(f"[SANDBOX] Function arguments: {arguments}")
                user_logs.append(f"[SANDBOX] Executing action: {function_name}")
                
                # Add assistant response to conversation with function call
                # For assistant messages with function calls, we need to handle them specially
                # Extract content if it exists, otherwise use empty string
                assistant_content = current_response.get("content", "")
                
                # Store assistant message with function call in a format OpenAI expects
                # We need to create a proper assistant message that OpenAI will accept
                function_call_data = {
                    "name": function_name,
                    "arguments": arguments_str
                }
                
                # Add the assistant message with the function call
                self.conversation.add_function_call("assistant", assistant_content, function_call_data)
                
                try:
                    # Execute the function (in sandbox mode only)
                    function_result = self.functions.execute(function_name, arguments, self.payment)
                    
                    # Log completion of function
                    logger.debug(f"[SANDBOX] Function result: {str(function_result)[:100]}...")
                    user_logs.append(f"[SANDBOX] Completed action: {function_name}")
                    
                    # Add function result to conversation
                    self.conversation.add_message("function", json.dumps(function_result), function_name)
                    
                except Exception as e:
                    # Handle function execution error
                    error_msg = f"Error executing PayPal function {function_name}: {str(e)}"
                    logger.error(error_msg)
                    user_logs.append(f"[SANDBOX] Error executing action: {function_name}")
                    
                    # Add error result to conversation
                    error_result = {"error": str(e), "status": "error"}
                    self.conversation.add_message("function", json.dumps(error_result), function_name)
                
                # Get next response from LLM
                logger.debug(f"[SANDBOX] Sending follow-up request to LLM (turn {turns}/{max_turns})")
                current_response = self.llm.get_completion(
                    messages=self.conversation.get_messages(),
                    functions=available_functions
                )
            
            # Add final assistant response to conversation
            if "content" in current_response and current_response["content"]:
                assistant_message = current_response["content"]
                self.conversation.add_message("assistant", assistant_message)
                
                # Add completion of request to user logs
                user_logs.append("[SANDBOX] Request processed successfully")
                
                # Return the final response
                logger.info(f"Generated response: {assistant_message[:50]}...")
                return {
                    "status": "success",
                    "response": assistant_message,
                    "user_logs": user_logs
                }
            elif "function_call" in current_response and turns >= max_turns:
                # Handle case where we've reached max turns but still have a function call
                logger.warning(f"[SANDBOX] Maximum function calls ({max_turns}) reached without final response")
                user_logs.append("[SANDBOX] Maximum PayPal API calls reached")
                
                # Force a final response without function calling
                logger.debug("[SANDBOX] Requesting final response without function calling")
                final_response = self.llm.get_completion(
                    messages=self.conversation.get_messages()
                )
                
                assistant_message = final_response.get("content", "I've reached the maximum number of PayPal API calls I can make in sandbox mode for this request.")
                self.conversation.add_message("assistant", assistant_message)
                
                return {
                    "status": "warning",
                    "response": assistant_message,
                    "user_logs": user_logs
                }
            else:
                # Handle unexpected response format
                error_message = "Unexpected response format from LLM"
                logger.error(error_message)
                user_logs.append("[SANDBOX] Error processing request")
                return {
                    "status": "error", 
                    "response": "I encountered an error while processing your request in PayPal sandbox mode.",
                    "user_logs": user_logs
                }
                
        except Exception as e:
            # Handle errors
            error_message = f"Error processing request: {str(e)}"
            logger.error(error_message)
            user_logs.append(f"[SANDBOX] Error processing request")
            return {
                "status": "error", 
                "response": f"I encountered an error while processing your request in PayPal sandbox mode: {str(e)}",
                "user_logs": user_logs
            }
    
    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.conversation.clear()
        logger.info("Cleared conversation history")

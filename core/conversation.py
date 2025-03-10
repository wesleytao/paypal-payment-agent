import json
import time
from typing import Dict, List, Any

class ConversationManager:
    """Manages conversation history and context."""
    
    def __init__(self, max_history: int = 100):
        self.history = []
        self.max_history = max_history
    
    def add_message(self, role: str, content: str, function_name: str = None) -> None:
        """Add a message to the conversation history.
        
        Args:
            role: The role of the message sender (user, assistant, function)
            content: The content of the message
            function_name: Optional function name, required if role is 'function'
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": time.time()
        }
        
        # Add function name if provided (required for function messages)
        if function_name is not None:
            message["name"] = function_name
        
        self.history.append(message)
        
        # Truncate history if needed
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def add_function_result(self, function_name: str, result: Any) -> None:
        """Add a function result to the conversation history.
        
        This is a convenience method that calls add_message with role='function'.
        
        Args:
            function_name: The name of the function that was called
            result: The result returned by the function
        """
        self.add_message("function", json.dumps(result), function_name)
        
    def add_function_call(self, role: str, content: str, function_call_data: Dict) -> None:
        """Add a message with a function call to the conversation history.
        
        This is specifically for assistant messages that include function calls.
        
        Args:
            role: The role of the message sender (typically 'assistant')
            content: The content of the message
            function_call_data: Dictionary with function call details including name and arguments
        """
        message = {
            "role": role,
            "content": content,
            "function_call": function_call_data,
            "timestamp": time.time()
        }
        
        self.history.append(message)
        
        # Truncate history if needed
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_messages(self) -> List[Dict]:
        """Get messages in format suitable for LLM API."""
        return [
            {
                "role": msg["role"],
                "content": msg["content"],
                **({"name": msg["name"]} if "name" in msg else {})
            }
            for msg in self.history
        ]
    
    def get_last_n_messages(self, n: int) -> List[Dict]:
        """Get the last n messages in format suitable for LLM API."""
        messages = self.get_messages()
        return messages[-n:] if n < len(messages) else messages
    
    def clear(self) -> None:
        """Clear conversation history."""
        self.history = []

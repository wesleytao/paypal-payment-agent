import json
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI
import os

from adapters.llm.base import LLMProvider
from config.settings import OPENAI_CONFIG, PROMPTS

logger = logging.getLogger(__name__)

class OpenAIAdapter(LLMProvider):
    """OpenAI implementation of LLM provider compatible with SDK v0.8.0."""
    
    def __init__(self):
        # Log OpenAI SDK version
        import pkg_resources
        openai_version = pkg_resources.get_distribution("openai").version
        logger.info(f"Using OpenAI SDK version: {openai_version}")
        
        # Get API key from environment or config
        direct_api_key = os.environ.get("OPENAI_API_KEY")
        if direct_api_key:
            api_key = direct_api_key
            logger.info("Using OPENAI_API_KEY from environment variable")
        else:
            # Fall back to config
            api_key = OPENAI_CONFIG["api_key"]
            logger.info("Using OPENAI_API_KEY from config settings")
        
        # Create the OpenAI client
        self.client = OpenAI(api_key=api_key)
        
        # Log key status (don't log the actual key)
        if not api_key or api_key.startswith(("YOUR_", "sk_test")):
            logger.error("OpenAI API key is missing or using placeholder value")
        
        # Get model from configuration
        self.model = OPENAI_CONFIG["model"]
        logger.info(f"Using model: {self.model}")
        
        # Note that we're only using PayPal REST API in sandbox mode
        logger.info(f"Initialized OpenAI adapter for PayPal REST API integration (sandbox mode only)")
    
    def get_completion(self, messages: List[Dict], functions: List[Dict] = None) -> Dict:
        """Get completion from OpenAI using the latest SDK (v1.x) with function calling."""
        try:
            logger.debug(f"Sending request to OpenAI with {len(messages)} messages")
            
            # Add system message if not present to ensure sandbox mode instructions
            if not messages or messages[0].get('role') != 'system':
                # Use the prompt from settings instead of hardcoding it
                messages = [PROMPTS["paypal_sandbox"]] + messages
            
            # Use the base class's logging method instead of individual log statements
            self.log_prompt(messages, functions, self.model)
            
            # Prepare tools if functions are provided (for function calling)
            tools = None
            if functions:
                tools = [
                    {"type": "function", "function": func}
                    for func in functions
                ]
                
            # Make API call with the modern Chat Completions API
            if tools:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto"
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
            
            # Process response
            first_choice = response.choices[0]
            message = first_choice.message
            
            # Check if the model wants to call a function
            if tools and hasattr(message, 'tool_calls') and message.tool_calls:
                # Return the function call details
                result = {
                    "role": "assistant",
                    "function_call": {
                        "name": message.tool_calls[0].function.name,
                        "arguments": message.tool_calls[0].function.arguments
                    }
                }
                # Log the response using the base class's method
                self.log_response(result)
                return result
            else:
                # Return the content
                content = message.content.strip() if message.content else ""
                result = {"role": "assistant", "content": content}
                # Log the response using the base class's method
                self.log_response(result)
                return result
            
        except Exception as e:
            error_msg = f"Error from OpenAI: {str(e)}"
            logger.error(error_msg)
            error_response = {"role": "assistant", "content": "I encountered an error while processing your request.", "error": str(e)}
            return error_response
    
    def _messages_to_prompt(self, messages: List[Dict]) -> str:
        """Convert a list of messages to a single prompt string."""
        prompt = ""
        
        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"
            elif role == "function":
                prompt += f"Function ({message.get('name', 'unknown')}): {content}\n\n"
        
        # Add a final prompt for the assistant to respond
        prompt += "Assistant: "
        
        return prompt

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import json
import logging
import uuid
import time

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Base interface for LLM providers."""
    
    def log_prompt(self, messages: List[Dict], functions: List[Dict] = None, model: str = None) -> None:
        """
        Log the prompt being sent to the LLM API.
        
        Args:
            messages: List of message objects with role and content
            functions: Optional list of function schemas for function calling
            model: Optional model name being used
        """
        # Generate a request ID and timestamp for correlation
        request_id = str(uuid.uuid4())[:8]  # Use shorter ID for readability
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # Log the main prompt information
            logger.info(f"[{request_id}] [{timestamp}] Sending prompt to LLM{' using model: ' + model if model else ''} for PayPal REST API (sandbox mode only)")
            
            # Log each message in the conversation with error handling
            for i, msg in enumerate(messages):
                try:
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    
                    # Log message details
                    logger.info(f"[{request_id}] Message {i} - Role: {role}")
                    if content:
                        # Handle long content
                        if len(content) > 500:
                            logger.info(f"[{request_id}] Content (truncated): {content[:500]}...")
                            logger.debug(f"[{request_id}] Full content: {content}")
                        else:
                            logger.info(f"[{request_id}] Content: {content}")
                    
                    # Log function calls in messages
                    if 'function_call' in msg:
                        func_call = msg['function_call']
                        logger.info(f"[{request_id}] Function call: {func_call.get('name')} with args: {func_call.get('arguments', '{}')}")
                except Exception as e:
                    # Catch and log any errors during message logging
                    logger.warning(f"[{request_id}] Error logging message {i}: {str(e)}")
            
            # Log functions being provided to the LLM
            if functions:
                logger.info(f"[{request_id}] Providing {len(functions)} functions to LLM for PayPal sandbox operations")
                for i, func in enumerate(functions):
                    try:
                        # Log function details safely
                        name = func.get('name', 'unnamed_function')
                        desc = func.get('description', '')[:100]
                        logger.info(f"[{request_id}] Function {i}: {name} - {desc}...")
                        
                        # Use safer JSON serialization with fallback
                        try:
                            # Convert non-serializable objects to strings
                            logger.debug(f"[{request_id}] Function definition: {json.dumps(func, default=str)}")
                        except Exception:
                            logger.debug(f"[{request_id}] Function definition: {str(func)}")
                    except Exception as e:
                        logger.warning(f"[{request_id}] Error logging function {i}: {str(e)}")
        except Exception as e:
            # Catch any overall errors in the logging process
            logger.error(f"Error during prompt logging: {str(e)}")
    
    def log_response(self, response: Dict) -> None:
        """
        Log the response received from the LLM API.
        
        Args:
            response: The response from the LLM
        """
        # Generate ID and timestamp for this log entry
        log_id = str(uuid.uuid4())[:8]
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            logger.info(f"[{log_id}] [{timestamp}] Received response from LLM")
            
            # Log content if present
            if "content" in response and response["content"]:
                content = response["content"]
                if len(content) > 500:
                    logger.info(f"[{log_id}] Response content (truncated): {content[:500]}...")
                    logger.debug(f"[{log_id}] Full response content: {content}")
                else:
                    logger.info(f"[{log_id}] Response content: {content}")
            
            # Log function call if present
            if "function_call" in response:
                func_call = response["function_call"]
                logger.info(f"[{log_id}] Response includes function call: {func_call.get('name')}")
                logger.debug(f"[{log_id}] Function arguments: {func_call.get('arguments', '{}')}")
        except Exception as e:
            logger.error(f"Error during response logging: {str(e)}")
    
    @abstractmethod
    def get_completion(self, messages: List[Dict], functions: List[Dict] = None) -> Dict:
        """
        Get completion from LLM with optional function calling.
        
        Args:
            messages: List of message objects with role and content
            functions: Optional list of function schemas for function calling
            
        Returns:
            Dict containing the LLM response with content and optional function call
        """
        pass

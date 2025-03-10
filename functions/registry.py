from typing import Dict, Callable, List, Any
import logging

logger = logging.getLogger(__name__)

class FunctionRegistry:
    """Registry for agent functions that can be called by the LLM."""
    
    def __init__(self):
        self.functions = {}
        self.schemas = {}
    
    def register(self, name: str, func: Callable, schema: Dict):
        """Register a function with its schema."""
        logger.info(f"Registering function: {name}")
        self.functions[name] = func
        self.schemas[name] = schema
    
    def get_function(self, name: str) -> Callable:
        """Get a function by name."""
        return self.functions.get(name)
    
    def get_schema(self, name: str) -> Dict:
        """Get a function schema by name."""
        return self.schemas.get(name)
    
    def get_schemas(self) -> List[Dict]:
        """Get all function schemas for LLM."""
        return list(self.schemas.values())
    
    def get_all_functions(self) -> List[Dict]:
        """Get all function schemas for LLM in the format required for OpenAI function calling.
        
        This is used by the ReAct pattern to provide available functions to the LLM.
        All functions are strictly limited to PayPal sandbox mode operations.
        """
        logger.debug(f"[SANDBOX] Retrieving {len(self.schemas)} available PayPal API functions")
        return list(self.schemas.values())
    
    def execute(self, name: str, arguments: Dict, payment_provider=None) -> Any:
        """Execute a function by name with arguments.
        
        Args:
            name: The name of the function to execute
            arguments: Dictionary of arguments to pass to the function
            payment_provider: Optional payment provider to use for execution
            
        Returns:
            Result of the function execution
        """
        func = self.get_function(name)
        if func:
            logger.info(f"[SANDBOX] Executing PayPal function: {name}")
            logger.debug(f"[SANDBOX] Function arguments: {arguments}")
            
            # If the function requires a payment provider, pass it as the first argument
            if payment_provider and "payment_provider" in func.__code__.co_varnames:
                return func(payment_provider, **arguments)
            else:
                return func(**arguments)
        
        logger.error(f"[SANDBOX] Function {name} not found in registry")
        return {"status": "error", "message": f"Function {name} not found in PayPal sandbox"}

import traceback
from typing import Dict, List, Optional, Any
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
import ast
import inspect

@dataclass
class DebugSession:
    session_id: str
    start_time: datetime
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    logs: List[str] = None

class DebuggingAgent:
    def __init__(self):
        self.current_session: Optional[DebugSession] = None
        self.sessions: Dict[str, DebugSession] = {}
        self.logger = self._setup_logger()
        self.breakpoints = set()
        self.watch_variables = set()

    def _setup_logger(self) -> logging.Logger:
        """Set up a logger for debugging"""
        logger = logging.getLogger('DebuggingAgent')
        logger.setLevel(logging.DEBUG)
        
        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

    def process_request(self, prompt: str):
        print(f"DebuggingAgent processing request: {prompt}")
        return "DebuggingAgent response"

    def start_debug_session(self, error: Exception) -> DebugSession:
        """Start a new debugging session for an error"""
        session_id = f"debug_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        session = DebugSession(
            session_id=session_id,
            start_time=datetime.utcnow(),
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            variables={},
            logs=[]
        )
        self.current_session = session
        self.sessions[session_id] = session
        return session

    def analyze_error(self, error: Exception) -> Dict[str, Any]:
        """Analyze an error and provide detailed information"""
        tb = traceback.extract_tb(error.__traceback__)
        analysis = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc(),
            "error_location": {
                "file": tb[-1].filename,
                "line": tb[-1].lineno,
                "function": tb[-1].name,
                "code": tb[-1].line
            }
        }
        return analysis

    def inspect_variable(self, variable: Any) -> Dict[str, Any]:
        """Inspect a variable and return its properties"""
        return {
            "type": type(variable).__name__,
            "value": str(variable),
            "attributes": dir(variable),
            "doc": getattr(variable, "__doc__", None),
            "module": getattr(variable, "__module__", None)
        }

    def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze code for potential issues"""
        try:
            tree = ast.parse(code)
            analysis = {
                "imports": [],
                "functions": [],
                "classes": [],
                "potential_issues": []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    analysis["imports"].extend(n.name for n in node.names)
                elif isinstance(node, ast.FunctionDef):
                    analysis["functions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append(node.name)
                
                # Check for potential issues
                if isinstance(node, ast.Try) and not node.handlers:
                    analysis["potential_issues"].append("Empty try-except block")
                if isinstance(node, ast.Except) and node.type is None:
                    analysis["potential_issues"].append("Bare except clause")
                
            return analysis
        except SyntaxError as e:
            return {"error": f"Syntax error: {str(e)}"}

    def set_breakpoint(self, filename: str, line: int):
        """Set a breakpoint at a specific line in a file"""
        self.breakpoints.add((filename, line))
        self.logger.info(f"Breakpoint set at {filename}:{line}")

    def watch_variable(self, variable_name: str):
        """Add a variable to the watch list"""
        self.watch_variables.add(variable_name)
        self.logger.info(f"Watching variable: {variable_name}")

    def get_call_stack(self) -> List[Dict[str, Any]]:
        """Get the current call stack"""
        stack = []
        for frame in inspect.stack()[1:]:  # Skip this function's frame
            stack.append({
                "filename": frame.filename,
                "function": frame.function,
                "line": frame.lineno,
                "code": frame.code_context[0] if frame.code_context else None,
                "locals": {name: str(val) for name, val in frame.frame.f_locals.items()}
            })
        return stack

    def get_debug_suggestions(self, error: Exception) -> List[str]:
        """Generate debugging suggestions based on the error"""
        suggestions = []
        error_type = type(error).__name__
        error_msg = str(error)

        if error_type == "NameError":
            suggestions.append("Check if all variables are properly defined")
            suggestions.append("Verify import statements")
        elif error_type == "TypeError":
            suggestions.append("Check the types of variables being used")
            suggestions.append("Verify function arguments")
        elif error_type == "IndexError":
            suggestions.append("Verify array/list indices")
            suggestions.append("Check if collections are empty")
        
        return suggestions

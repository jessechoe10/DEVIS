from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class Endpoint:
    path: str
    method: str
    handler: callable
    middleware: List[callable] = None

class BackendAgent:
    def __init__(self):
        self.endpoints: Dict[str, Endpoint] = {}
        self.middleware_stack = []
        self.data_processors = {}

    def process_request(self, prompt: str):
        print(f"BackendAgent processing request: {prompt}")
        return "BackendAgent response"

    def register_endpoint(self, path: str, method: str, handler: callable, middleware: List[callable] = None):
        endpoint = Endpoint(path, method.upper(), handler, middleware or [])
        self.endpoints[f"{method.upper()}:{path}"] = endpoint
        return endpoint

    def add_middleware(self, middleware: callable):
        self.middleware_stack.append(middleware)

    def process_request_with_middleware(self, request: Dict[str, Any]) -> Dict[str, Any]:
        current_request = request
        for middleware in self.middleware_stack:
            current_request = middleware(current_request)
        return current_request

    def register_data_processor(self, name: str, processor: callable):
        self.data_processors[name] = processor

    def process_data(self, data: Any, processor_name: str) -> Any:
        if processor_name not in self.data_processors:
            raise ValueError(f"No processor registered with name: {processor_name}")
        return self.data_processors[processor_name](data)

    def validate_request(self, request: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        try:
            for field, field_type in schema.items():
                if field not in request:
                    return False
                if not isinstance(request[field], field_type):
                    return False
            return True
        except Exception:
            return False

    def format_response(self, data: Any, status: int = 200, message: str = "Success") -> Dict[str, Any]:
        return {
            "status": status,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

    def handle_error(self, error: Exception) -> Dict[str, Any]:
        return {
            "status": 500,
            "message": str(error),
            "error_type": error.__class__.__name__,
            "timestamp": datetime.utcnow().isoformat()
        }

"""Protocol Standard for Robot Communication"""

from enum import Enum
from typing import Dict, Any, Optional
import json


class ProtocolCommand(Enum):
    """Standard protocol commands"""
    START = "START"
    STOP = "STOP"
    MOVE_FORWARD = "MOVE_FORWARD"
    LIFT = "LIFT"
    FLY = "FLY"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    STATUS_REQUEST = "STATUS_REQUEST"
    SET_COURSE = "SET_COURSE"


class ProtocolHandler:
    """
    Handles protocol-based communication for robot control.
    Provides standardized message format for commands and responses.
    """
    
    PROTOCOL_VERSION = "1.0"
    
    @staticmethod
    def create_command(command: ProtocolCommand, parameters: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a protocol-compliant command message.
        
        Args:
            command: The command to execute
            parameters: Optional parameters for the command
            
        Returns:
            JSON-encoded command string
        """
        message = {
            'protocol_version': ProtocolHandler.PROTOCOL_VERSION,
            'command': command.value,
            'parameters': parameters or {},
            'timestamp': None  # Would use actual timestamp in production
        }
        return json.dumps(message)
    
    @staticmethod
    def parse_command(message: str) -> Dict[str, Any]:
        """
        Parse a protocol command message.
        
        Args:
            message: JSON-encoded command string
            
        Returns:
            Parsed command dictionary
        """
        try:
            data = json.loads(message)
            
            # Validate protocol version
            if data.get('protocol_version') != ProtocolHandler.PROTOCOL_VERSION:
                raise ValueError(f"Unsupported protocol version: {data.get('protocol_version')}")
            
            return {
                'command': ProtocolCommand(data['command']),
                'parameters': data.get('parameters', {}),
                'timestamp': data.get('timestamp')
            }
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Invalid protocol message: {e}")
    
    @staticmethod
    def create_response(status: str, data: Optional[Dict[str, Any]] = None, error: Optional[str] = None) -> str:
        """
        Create a protocol-compliant response message.
        
        Args:
            status: Response status ('success', 'error', 'pending')
            data: Optional response data
            error: Optional error message
            
        Returns:
            JSON-encoded response string
        """
        message = {
            'protocol_version': ProtocolHandler.PROTOCOL_VERSION,
            'status': status,
            'data': data or {},
            'error': error,
            'timestamp': None  # Would use actual timestamp in production
        }
        return json.dumps(message)
    
    @staticmethod
    def parse_response(message: str) -> Dict[str, Any]:
        """
        Parse a protocol response message.
        
        Args:
            message: JSON-encoded response string
            
        Returns:
            Parsed response dictionary
        """
        try:
            data = json.loads(message)
            
            # Validate protocol version
            if data.get('protocol_version') != ProtocolHandler.PROTOCOL_VERSION:
                raise ValueError(f"Unsupported protocol version: {data.get('protocol_version')}")
            
            return {
                'status': data['status'],
                'data': data.get('data', {}),
                'error': data.get('error'),
                'timestamp': data.get('timestamp')
            }
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid protocol message: {e}")

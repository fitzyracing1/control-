"""Movement System with Ground, Lift, and Flight Capabilities"""

import time
import threading
from enum import Enum
from typing import Tuple


class MovementMode(Enum):
    """Movement modes for the robot"""
    GROUND = "ground"
    LIFTING = "lifting"
    FLIGHT = "flight"
    STOPPED = "stopped"


class MovementSystem:
    """
    Handles all robot movement including ground navigation, lift, and flight.
    Maintains continuous autonomous operation across mode transitions.
    """
    
    def __init__(self):
        self.mode = MovementMode.STOPPED
        self.autonomous_active = False
        self.position = [0.0, 0.0, 0.0]  # [x, y, z]
        self.velocity = [0.0, 0.0, 0.0]  # [vx, vy, vz]
        self._lock = threading.Lock()
        
    def set_mode(self, mode: MovementMode):
        """Set the movement mode"""
        with self._lock:
            print(f"Movement mode changed: {self.mode.value} -> {mode.value}")
            self.mode = mode
    
    def get_mode(self) -> MovementMode:
        """Get current movement mode"""
        return self.mode
    
    def start_autonomous(self):
        """Start autonomous operation"""
        with self._lock:
            self.autonomous_active = True
            print("Autonomous operation started")
    
    def stop_autonomous(self):
        """Stop autonomous operation"""
        with self._lock:
            self.autonomous_active = False
            print("Autonomous operation stopped")
    
    def is_autonomous_active(self) -> bool:
        """Check if autonomous operation is active"""
        return self.autonomous_active
    
    def move_forward(self, speed: float = 1.0):
        """
        Execute forward movement.
        Speed is normalized (0.0 to 2.0, where 1.0 is nominal).
        """
        if not self.autonomous_active:
            return
        
        with self._lock:
            # Update velocity
            self.velocity[0] = speed
            
            # Update position (simplified physics)
            dt = 0.05  # Assume 20Hz update rate
            self.position[0] += self.velocity[0] * dt
            
            if self.mode == MovementMode.GROUND:
                # Ground-specific movement
                pass
            elif self.mode == MovementMode.LIFTING:
                # Continue forward movement during lift
                pass
            elif self.mode == MovementMode.FLIGHT:
                # Flight-specific forward movement
                pass
    
    def lift(self, speed: float = 0.5):
        """
        Execute vertical lift.
        Maintains forward autonomous movement simultaneously.
        """
        if not self.autonomous_active:
            return
        
        with self._lock:
            # Update vertical velocity
            self.velocity[2] = speed
            
            # Update altitude
            dt = 0.05
            self.position[2] += self.velocity[2] * dt
            
            print(f"Lifting: altitude={self.position[2]:.2f}m")
    
    def fly_autonomous(self, direction: str = 'forward', speed: float = 1.5, altitude: float = 10.0):
        """
        Execute autonomous flight operations.
        Maintains altitude while navigating autonomously.
        """
        if not self.autonomous_active:
            return
        
        with self._lock:
            # Maintain target altitude
            altitude_error = altitude - self.position[2]
            self.velocity[2] = altitude_error * 0.1  # Simple proportional control
            
            # Continue forward autonomous movement
            self.velocity[0] = speed
            
            # Update position
            dt = 0.05
            self.position[0] += self.velocity[0] * dt
            self.position[2] += self.velocity[2] * dt
    
    def get_altitude(self) -> float:
        """Get current altitude"""
        return self.position[2]
    
    def get_position(self) -> Tuple[float, float, float]:
        """Get current position (x, y, z)"""
        return tuple(self.position)
    
    def emergency_stop(self):
        """Emergency stop - halt all movement"""
        with self._lock:
            self.mode = MovementMode.STOPPED
            self.autonomous_active = False
            self.velocity = [0.0, 0.0, 0.0]
            print("EMERGENCY STOP: All movement halted")
    
    def stop(self):
        """Graceful stop of movement system"""
        self.stop_autonomous()
        with self._lock:
            self.mode = MovementMode.STOPPED
            self.velocity = [0.0, 0.0, 0.0]

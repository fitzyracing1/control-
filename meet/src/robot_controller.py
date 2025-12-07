"""Main Robot Controller with Autonomous Movement Capabilities"""

import threading
import time
from enum import Enum
from typing import Optional, Tuple
from .signal_processor import SignalProcessor
from .movement_system import MovementSystem, MovementMode


class RobotState(Enum):
    """Robot operational states"""
    IDLE = "idle"
    GROUND_AUTONOMOUS = "ground_autonomous"
    LIFTING = "lifting"
    FLIGHT_AUTONOMOUS = "flight_autonomous"
    EMERGENCY_STOP = "emergency_stop"


class RobotController:
    """
    Main controller for autonomous robot with lift and flight capabilities.
    Maintains continuous autonomous operation across all movement modes.
    """
    
    def __init__(self):
        self.state = RobotState.IDLE
        self.signal_processor = SignalProcessor()
        self.movement_system = MovementSystem()
        self._running = False
        self._lock = threading.Lock()
        self._control_thread: Optional[threading.Thread] = None
        
    def start(self):
        """Start the autonomous robot control system"""
        with self._lock:
            if self._running:
                print("Robot controller already running")
                return
            
            self._running = True
            self._control_thread = threading.Thread(target=self._control_loop, daemon=True)
            self._control_thread.start()
            print("Robot controller started")
    
    def stop(self):
        """Stop the robot control system"""
        with self._lock:
            self._running = False
        
        if self._control_thread:
            self._control_thread.join(timeout=5.0)
        
        self.movement_system.stop()
        print("Robot controller stopped")
    
    def _control_loop(self):
        """Main control loop - maintains autonomous operation"""
        print("Autonomous control loop started")
        
        while self._running:
            try:
                # Process future signals to plan course
                future_course = self.signal_processor.process_future_signals()
                
                # Execute autonomous movement based on current state
                if self.state == RobotState.IDLE:
                    self._transition_to_ground_autonomous()
                
                elif self.state == RobotState.GROUND_AUTONOMOUS:
                    self._execute_ground_autonomous(future_course)
                    
                    # Check if conditions met to initiate lift
                    if self._should_initiate_lift(future_course):
                        self._transition_to_lifting()
                
                elif self.state == RobotState.LIFTING:
                    self._execute_lift_sequence(future_course)
                
                elif self.state == RobotState.FLIGHT_AUTONOMOUS:
                    self._execute_flight_autonomous(future_course)
                
                time.sleep(0.05)  # 20Hz control loop
                
            except Exception as e:
                print(f"Error in control loop: {e}")
                self._emergency_stop()
    
    def _transition_to_ground_autonomous(self):
        """Transition from idle to ground autonomous movement"""
        print("Transitioning to ground autonomous mode")
        self.state = RobotState.GROUND_AUTONOMOUS
        self.movement_system.set_mode(MovementMode.GROUND)
        self.movement_system.start_autonomous()
    
    def _execute_ground_autonomous(self, future_course: dict):
        """Execute autonomous forward movement on ground"""
        # Extract course information
        direction = future_course.get('direction', 'forward')
        speed = future_course.get('speed', 1.0)
        
        # Command autonomous forward movement
        self.movement_system.move_forward(speed)
    
    def _should_initiate_lift(self, future_course: dict) -> bool:
        """Determine if robot should initiate lift sequence"""
        # Check signal processor for lift trigger
        return future_course.get('lift_command', False)
    
    def _transition_to_lifting(self):
        """Transition to lift mode while maintaining autonomy"""
        print("Initiating lift sequence - maintaining autonomous operation")
        self.state = RobotState.LIFTING
        # Note: Autonomous operation continues during lift
    
    def _execute_lift_sequence(self, future_course: dict):
        """Execute vertical lift while continuing autonomous forward movement"""
        lift_height = future_course.get('target_altitude', 10.0)
        
        # Simultaneously execute lift and maintain forward autonomous movement
        self.movement_system.set_mode(MovementMode.LIFTING)
        current_altitude = self.movement_system.get_altitude()
        
        if current_altitude < lift_height:
            # Continue forward movement while lifting
            self.movement_system.lift(future_course.get('lift_speed', 0.5))
            self.movement_system.move_forward(future_course.get('speed', 1.0))
        else:
            # Transition to flight mode
            self._transition_to_flight()
    
    def _transition_to_flight(self):
        """Transition to flight mode - autonomous operation never stops"""
        print("Transitioning to flight mode - continuous autonomous operation")
        self.state = RobotState.FLIGHT_AUTONOMOUS
        self.movement_system.set_mode(MovementMode.FLIGHT)
    
    def _execute_flight_autonomous(self, future_course: dict):
        """Execute autonomous flight operations"""
        # Extract flight parameters from future signals
        direction = future_course.get('direction', 'forward')
        speed = future_course.get('speed', 1.5)
        altitude = future_course.get('target_altitude', 10.0)
        
        # Maintain autonomous flight
        self.movement_system.fly_autonomous(
            direction=direction,
            speed=speed,
            altitude=altitude
        )
    
    def _emergency_stop(self):
        """Emergency stop procedure"""
        print("EMERGENCY STOP ACTIVATED")
        self.state = RobotState.EMERGENCY_STOP
        self.movement_system.emergency_stop()
        self._running = False
    
    def get_status(self) -> dict:
        """Get current robot status"""
        return {
            'state': self.state.value,
            'movement_mode': self.movement_system.get_mode().value,
            'altitude': self.movement_system.get_altitude(),
            'position': self.movement_system.get_position(),
            'is_autonomous': self.movement_system.is_autonomous_active()
        }

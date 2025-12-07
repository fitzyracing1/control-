"""Main entry point for Autonomous Robot Protocol Standard Bot"""

import time
import signal
import sys
from src.robot_controller import RobotController
from src.protocol_handler import ProtocolHandler, ProtocolCommand


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nShutdown signal received...")
    if 'robot' in globals():
        robot.stop()
    sys.exit(0)


def main():
    """Main function to run the autonomous robot"""
    print("=" * 60)
    print("Autonomous Robot Protocol Standard Bot")
    print("=" * 60)
    print("Features:")
    print("  - Signal processing for future course planning")
    print("  - Autonomous forward movement")
    print("  - Vertical lift with continuous autonomy")
    print("  - Flight mode with full autonomous operation")
    print("  - Protocol-based communication standard")
    print("=" * 60)
    print()
    
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and start robot controller
    global robot
    robot = RobotController()
    
    print("Starting robot controller...")
    robot.start()
    
    print("\nRobot is now operating autonomously!")
    print("Press Ctrl+C to stop\n")
    
    # Main monitoring loop
    try:
        while True:
            # Get and display status every 2 seconds
            status = robot.get_status()
            
            print(f"Status: {status['state']:20s} | "
                  f"Mode: {status['movement_mode']:10s} | "
                  f"Alt: {status['altitude']:6.2f}m | "
                  f"Pos: ({status['position'][0]:6.2f}, {status['position'][1]:6.2f}, {status['position'][2]:6.2f}) | "
                  f"Auto: {'YES' if status['is_autonomous'] else 'NO'}")
            
            time.sleep(2.0)
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        robot.stop()
        print("Robot stopped successfully")
    except Exception as e:
        print(f"\nError: {e}")
        robot.stop()
        sys.exit(1)


def demonstrate_protocol():
    """Demonstrate the protocol standard"""
    print("\n" + "=" * 60)
    print("Protocol Standard Demonstration")
    print("=" * 60)
    
    # Create example commands
    start_cmd = ProtocolHandler.create_command(ProtocolCommand.START)
    print(f"\nSTART Command: {start_cmd}")
    
    move_cmd = ProtocolHandler.create_command(
        ProtocolCommand.MOVE_FORWARD,
        {'speed': 1.5, 'duration': 10.0}
    )
    print(f"MOVE Command: {move_cmd}")
    
    lift_cmd = ProtocolHandler.create_command(
        ProtocolCommand.LIFT,
        {'target_altitude': 10.0, 'lift_speed': 0.5}
    )
    print(f"LIFT Command: {lift_cmd}")
    
    # Create example response
    response = ProtocolHandler.create_response(
        'success',
        data={'position': [100.0, 0.0, 10.0], 'state': 'flight_autonomous'}
    )
    print(f"\nSuccess Response: {response}")
    print("=" * 60)


if __name__ == "__main__":
    # Uncomment to see protocol demonstration
    # demonstrate_protocol()
    
    main()

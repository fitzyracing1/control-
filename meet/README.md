# Autonomous Robot Protocol Standard Bot

An advanced protocol-based autonomous robot control system with seamless ground navigation, lift, and flight capabilities.

## Features

- **Signal Processing**: Links future signals to specific robot movement courses
- **Autonomous Forward Movement**: Continuous autonomous navigation on ground
- **Vertical Lift**: Seamless transition to vertical lift while maintaining autonomous operation
- **Flight Mode**: Full autonomous flight capabilities with continuous operation
- **Protocol Standard**: Standardized communication protocol for robot commands and responses
- **Continuous Autonomy**: Never stops being autonomous during mode transitions

## Project Structure

```
meet/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── robot_controller.py      # Main robot controller with state machine
│   ├── signal_processor.py      # Future course signal processing
│   ├── movement_system.py       # Ground, lift, and flight movement
│   └── protocol_handler.py      # Protocol standard for communication
├── main.py                       # Entry point for robot operation
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Architecture

### Robot Controller
The main controller (`RobotController`) manages the robot's operational states:
- **IDLE**: Initial state
- **GROUND_AUTONOMOUS**: Autonomous forward movement on ground
- **LIFTING**: Vertical lift while maintaining forward autonomy
- **FLIGHT_AUTONOMOUS**: Full autonomous flight operation
- **EMERGENCY_STOP**: Safety stop state

### Signal Processor
Processes future signals and links them to specific movement commands:
- Analyzes incoming signals
- Plans future robot course
- Generates movement parameters
- Maintains course history

### Movement System
Handles all physical movement across modes:
- Ground navigation
- Vertical lift operations
- Flight control
- Maintains continuous autonomous operation during transitions

### Protocol Handler
Standardized communication protocol:
- Command encoding/decoding
- Response formatting
- Version management
- Error handling

## Getting Started

### Prerequisites
- Python 3.7 or higher
- No external dependencies required for basic operation

### Installation

1. Navigate to the project directory:
```bash
cd /Users/joshuafitzgerald/meet
```

2. (Optional) Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies (if any):
```bash
pip install -r requirements.txt
```

### Running the Robot

Start the autonomous robot:
```bash
python3 main.py
```

The robot will:
1. Start in IDLE state
2. Transition to autonomous ground movement
3. Process future signals for course planning
4. Execute lift sequence when triggered
5. Transition to autonomous flight mode
6. Maintain continuous autonomous operation throughout

Press `Ctrl+C` to gracefully stop the robot.

## Usage Examples

### Basic Operation
```python
from src.robot_controller import RobotController

# Create and start robot
robot = RobotController()
robot.start()

# Robot now operates autonomously
# Monitor status
status = robot.get_status()
print(status)

# Stop when done
robot.stop()
```

### Protocol Commands
```python
from src.protocol_handler import ProtocolHandler, ProtocolCommand

# Create command
cmd = ProtocolHandler.create_command(
    ProtocolCommand.MOVE_FORWARD,
    {'speed': 1.5}
)

# Parse command
parsed = ProtocolHandler.parse_command(cmd)
```

## Key Concepts

### Continuous Autonomy
The robot maintains autonomous operation through all transitions:
- Ground → Lift: Forward movement continues during vertical lift
- Lift → Flight: Seamless transition with no autonomy interruption
- Flight: Full 3D autonomous navigation

### Future Signal Processing
The signal processor links incoming signals to specific robot courses:
- Analyzes signal patterns
- Plans optimal trajectory
- Generates movement commands
- Adapts to changing conditions

### Thread-Safe Operation
All components use proper locking mechanisms for safe concurrent operation:
- Signal processing runs independently
- Movement system updates safely
- State transitions are atomic

## Safety Features

- Emergency stop capability
- State-based error handling
- Graceful shutdown on errors
- Thread-safe operations

## Development

### Adding New Movement Modes
1. Add mode to `MovementMode` enum
2. Implement mode logic in `MovementSystem`
3. Add state to `RobotState` enum
4. Update controller state machine

### Extending Protocol
1. Add command to `ProtocolCommand` enum
2. Implement handler in controller
3. Update protocol documentation

## License

MIT License - See LICENSE file for details

## Author

Your Name

## Version

0.1.0

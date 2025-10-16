# Traffic Control System for Raspberry Pi

A fully functioning traffic control system for a 2-lane road intersection with V (Vertical) and H (Horizontal) streets.

## Features

- **Two Streets**: V-Street (Vertical) and H-Street (Horizontal), both 2-laned
- **Complete Traffic Light Control**: Red, Yellow, and Green lights for each street
- **Time Schedule**: 
  - Red: 12 seconds
  - Green: 9 seconds
  - Yellow: 3 seconds
  - Total cycle: 24 seconds per direction

## Hardware Requirements

### Components Needed:
- 1x Raspberry Pi (any model with GPIO pins)
- 6x LEDs (2 Red, 2 Yellow, 2 Green)
- 6x 220Ω - 330Ω Resistors (current limiting resistors for LEDs)
- 1x Breadboard
- Jumper wires (male-to-female and male-to-male)
- Power supply for Raspberry Pi

## GPIO Pin Configuration

### Vertical Street (V)
- **Red LED**: GPIO 17
- **Yellow LED**: GPIO 27
- **Green LED**: GPIO 22

### Horizontal Street (H)
- **Red LED**: GPIO 23
- **Yellow LED**: GPIO 24
- **Green LED**: GPIO 25

## Circuit Diagram

```
Raspberry Pi GPIO Layout:

V-Street:                    H-Street:
GPIO 17 (Red) ---[220Ω]---> LED --> GND
GPIO 27 (Yellow) -[220Ω]---> LED --> GND
GPIO 22 (Green) --[220Ω]---> LED --> GND

GPIO 23 (Red) ---[220Ω]---> LED --> GND
GPIO 24 (Yellow) -[220Ω]---> LED --> GND
GPIO 25 (Green) --[220Ω]---> LED --> GND
```

### Wiring Instructions:
1. Connect the anode (+) of each LED to its respective GPIO pin through a 220Ω resistor
2. Connect the cathode (-) of each LED to any GND pin on the Raspberry Pi
3. Make sure all connections are secure

## Installation

### 1. Setup Raspberry Pi

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3 (if not already installed)
sudo apt-get install python3 python3-pip -y

# Install RPi.GPIO library
sudo apt-get install python3-rpi.gpio -y
# OR
pip3 install RPi.GPIO
```

### 2. Clone/Copy the Project

```bash
# Navigate to your project directory
cd ~/
mkdir robotics-mini-project
cd robotics-mini-project

# Copy main.py to this directory
```

### 3. Set Permissions

```bash
# Make sure the script has execute permissions
chmod +x main.py
```

## Usage

### Running the System

```bash
# Run with Python 3
python3 main.py

# OR run with sudo if you encounter permission issues
sudo python3 main.py
```

### Stopping the System

- Press `Ctrl + C` to safely stop the system
- The system will automatically turn all lights to red, then turn them off
- GPIO pins will be cleaned up automatically

## System Operation

### Traffic Light Cycle

The system operates in two phases:

**Phase 1: H-Street Active (12 seconds)**
- V-Street: RED (12s)
- H-Street: GREEN (9s) → YELLOW (3s)

**Phase 2: V-Street Active (12 seconds)**
- V-Street: GREEN (9s) → YELLOW (3s)
- H-Street: RED (12s)

Total cycle time: 24 seconds

### Startup Sequence
- System flashes all yellow lights 3 times to indicate startup
- Then begins normal operation

### Shutdown Sequence
- All lights turn RED for 2 seconds (safety measure)
- All lights turn OFF
- GPIO pins are cleaned up

## Customization

### Changing Timing

Edit the timing constants in `main.py`:

```python
# Timing Configuration (in seconds)
RED_TIME = 12
GREEN_TIME = 9
YELLOW_TIME = 3
```

### Changing GPIO Pins

Edit the pin configuration in `main.py`:

```python
# GPIO Pin Configuration
V_RED_PIN = 17
V_YELLOW_PIN = 27
V_GREEN_PIN = 22

H_RED_PIN = 23
H_YELLOW_PIN = 24
H_GREEN_PIN = 25
```

## Troubleshooting

### GPIO Permission Errors
If you get permission errors, run with sudo:
```bash
sudo python3 main.py
```

### LEDs Not Lighting Up
1. Check all wiring connections
2. Verify resistor values (220Ω - 330Ω)
3. Test LEDs individually with a battery
4. Check GPIO pin numbers match your wiring

### Import Errors
If you get "ImportError: No module named RPi.GPIO":
```bash
sudo apt-get install python3-rpi.gpio
# OR
pip3 install RPi.GPIO
```

## Safety Notes

- Always shutdown the system properly using Ctrl+C
- Don't disconnect wiring while the system is running
- Use appropriate resistors to prevent LED burnout
- Keep the Raspberry Pi in a safe, ventilated area

## License

This project is open source and available for educational purposes.

## Author

Created for robotics mini-project demonstration.

# Pedestrian Crossing Feature 🚶

## Overview

The traffic control system now includes pedestrian crossing features for **BOTH streets**:
- **V-Street**: Activated by pressing the **'O' key**
- **H-Street**: Activated by pressing the **'P' key**

Pedestrians can request a crossing, and the system will activate the WALK signal **only when the respective street has a RED light** (safe to cross).

## Features

✅ **Safe Crossing**: Only activates when the respective street's traffic light is RED  
✅ **9-Second Walk Time**: Pedestrians get 9 seconds out of the 12-second red light to cross  
✅ **Dual Crossing Support**: Independent pedestrian signals for both V-Street and H-Street  
✅ **Visual Feedback**: Clear messages with emojis showing WALK 🟢 and STOP 🔴 status  
✅ **Request Queueing**: Requests are remembered and activated during the next RED phase  

## Hardware Components

### Additional Components for Pedestrian Signals:
- 4x LEDs total:
  - 2x Green LEDs (WALK signals)
  - 2x Red LEDs (DON'T WALK signals)
- 4x 220Ω Resistors

### GPIO Pin Assignment:
**V-Street Pedestrian Crossing:**
- **PEDESTRIAN_V_WALK_PIN** = GPIO 10 (Green "WALK" LED)
- **PEDESTRIAN_V_STOP_PIN** = GPIO 9 (Red "DON'T WALK" LED)

**H-Street Pedestrian Crossing:**
- **PEDESTRIAN_H_WALK_PIN** = GPIO 11 (Green "WALK" LED)
- **PEDESTRIAN_H_STOP_PIN** = GPIO 8 (Red "DON'T WALK" LED)

## Wiring Diagram

```
PEDESTRIAN SIGNAL CONNECTIONS:
================================

V-Street Pedestrian Crossing:
GPIO 10 --> [220Ω Resistor] --> Green LED (+) --> LED (-) --> GND
GPIO 9  --> [220Ω Resistor] --> Red LED (+)   --> LED (-) --> GND

H-Street Pedestrian Crossing:
GPIO 11 --> [220Ω Resistor] --> Green LED (+) --> LED (-) --> GND
GPIO 8  --> [220Ω Resistor] --> Red LED (+)   --> LED (-) --> GND


COMPLETE SYSTEM:
================

V-Street Traffic:         GPIO 17 (Red), GPIO 27 (Yellow), GPIO 22 (Green)
H-Street Traffic:         GPIO 23 (Red), GPIO 24 (Yellow), GPIO 25 (Green)
V-Street Pedestrian:      GPIO 10 (Walk/Green), GPIO 9 (Stop/Red)
H-Street Pedestrian:      GPIO 11 (Walk/Green), GPIO 8 (Stop/Red)

Total LEDs: 10 (6 traffic + 4 pedestrian)
Total GPIO pins used: 10
```

## How It Works

### Normal Operation:
1. Both pedestrian STOP signals (red) are ON by default
2. Traffic cycles normally through phases

### When 'O' Key is Pressed (V-Street Crossing):
1. System registers V-Street pedestrian crossing request
2. Request is queued until V-Street light turns RED
3. When V-Street is RED (Phase 1):
   - V-Street STOP signal turns OFF
   - V-Street WALK signal turns ON 🟢
   - Pedestrian has 9 seconds to cross V-Street
   - After 9 seconds, WALK turns OFF, STOP turns ON 🔴

### When 'P' Key is Pressed (H-Street Crossing):
1. System registers H-Street pedestrian crossing request
2. Request is queued until H-Street light turns RED
3. When H-Street is RED (Phase 2):
   - H-Street STOP signal turns OFF
   - H-Street WALK signal turns ON 🟢
   - Pedestrian has 9 seconds to cross H-Street
   - After 9 seconds, WALK turns OFF, STOP turns ON 🔴

### Safety Rules:
- ✅ V-Street pedestrian crossing ONLY activates during V-Street RED phase
- ✅ H-Street pedestrian crossing ONLY activates during H-Street RED phase
- ✅ If pressed during GREEN/YELLOW, request is saved for next RED phase
- ✅ Walk time: 9 seconds (sufficient for safe crossing)
- ✅ Opposite street traffic continues normally during pedestrian crossing
- ✅ Independent operation - both crossings can be requested in the same cycle

## Timing Breakdown

```
PHASE 1: V-Street RED, H-Street Active
═══════════════════════════════════════════════════════
Time    V-Street    H-Street    V-Ped           H-Ped
0s      🔴 RED      🟢 GREEN    [Can request]   🔴 STOP
0s-9s   🔴 RED      🟢 GREEN    🟢 WALK (9s)    🔴 STOP
9s      🔴 RED      🟡 YELLOW   🔴 STOP         🔴 STOP
12s     🔴 RED      🔴 RED      🔴 STOP         🔴 STOP

PHASE 2: V-Street Active, H-Street RED
═══════════════════════════════════════════════════════
Time    V-Street    H-Street    V-Ped           H-Ped
0s      🟢 GREEN    🔴 RED      🔴 STOP         [Can request]
0s-9s   🟢 GREEN    🔴 RED      🔴 STOP         🟢 WALK (9s)
9s-12s  🟡 YELLOW   🔴 RED      🔴 STOP         🔴 STOP
```

## Usage

### On Windows (Simulation):
```powershell
python main.py

# Press 'O' key at any time to request V-Street pedestrian crossing
# Press 'P' key at any time to request H-Street pedestrian crossing
# Watch for: 🚶 [PEDESTRIAN REQUEST] Crossing requested on [Street]!
```

### On Raspberry Pi:
```bash
sudo python3 main.py

# Press 'O' key to request V-Street crossing
# Press 'P' key to request H-Street crossing
# Respective Green WALK LED will light up when safe
```

## Installation

### Install Required Library:
```bash
pip install keyboard
# OR on Raspberry Pi:
pip3 install keyboard
```

This library is included in `requirements.txt`:
```
RPi.GPIO>=0.7.1
keyboard>=0.13.5
```

## Example Output

```
============================================================
CYCLE 1 - 2025-10-16 14:10:52
============================================================

--- PHASE 1: H-Street Active (V-Street 🔴 RED) ---
[14:10:52] V-Street (Vertical): RED 🔴
[14:10:52] H-Street (Horizontal): GREEN 🟢

🚶 [PEDESTRIAN REQUEST] Crossing requested on V-Street!
🚶 Activating V-Street pedestrian crossing for 9 seconds...
🚶 [14:10:52] V-STREET PEDESTRIAN WALK ACTIVE 🟢 - Cross V-Street NOW!
🚶 [14:11:01] V-STREET PEDESTRIAN WALK ENDED 🔴 - Do NOT cross!

    H-Street: GREEN 🟢 → YELLOW 🟡
[14:11:01] H-Street (Horizontal): YELLOW 🟡

--- PHASE 2: V-Street Active (H-Street 🔴 RED) ---
[14:11:05] V-Street (Vertical): GREEN 🟢
[14:11:05] H-Street (Horizontal): RED 🔴

🚶 [PEDESTRIAN REQUEST] Crossing requested on H-Street!
🚶 Activating H-Street pedestrian crossing for 9 seconds...
🚶 [14:11:05] H-STREET PEDESTRIAN WALK ACTIVE 🟢 - Cross H-Street NOW!
🚶 [14:11:14] H-STREET PEDESTRIAN WALK ENDED 🔴 - Do NOT cross!
```

## Safety Features

### 1. **Request Validation**
- V-Street: Only processes requests when V-Street is RED
- H-Street: Only processes requests when H-Street is RED
- Ignores requests during unsafe periods

### 2. **Clear Visual Signals**
- WALK 🟢: Safe to cross the respective street
- STOP 🔴: Do NOT cross

### 3. **Adequate Crossing Time**
- 9 seconds is sufficient for pedestrians to safely cross a 2-lane street
- Based on standard walking speed of ~1.2 m/s

### 4. **No Traffic Disruption**
- V-Street pedestrian crossing doesn't interfere with normal traffic flow
- H-Street pedestrian crossing doesn't interfere with normal traffic flow
- Opposite street traffic continues normally during pedestrian crossing

### 5. **Independent Operation**
- Both crossings work independently
- Can request both in the same cycle
- Each activates only when its street is RED

## Customization

### Change Walk Time:
Edit in `main.py`:
```python
PEDESTRIAN_WALK_TIME = 9  # Change to desired seconds (max 12)
```

### Change GPIO Pins:
```python
# V-Street Pedestrian Crossing
PEDESTRIAN_V_WALK_PIN = 10   # Green WALK signal
PEDESTRIAN_V_STOP_PIN = 9    # Red STOP signal

# H-Street Pedestrian Crossing
PEDESTRIAN_H_WALK_PIN = 11   # Green WALK signal
PEDESTRIAN_H_STOP_PIN = 8    # Red STOP signal
```

## Troubleshooting

### Keyboard Library Not Working:
```bash
pip install keyboard --upgrade
# On some systems, may need admin/sudo:
sudo pip3 install keyboard
```

### On Linux/Raspberry Pi Permission Issues:
```bash
# Run with sudo for keyboard access:
sudo python3 main.py
```

### 'O' or 'P' Key Not Responding:
- Make sure terminal window is focused
- Keyboard library needs administrator privileges on some systems
- Try running with `sudo` on Raspberry Pi

### Pedestrian Signal Not Activating:
- V-Street: Check that 'O' is pressed during V-Street RED phase
- H-Street: Check that 'P' is pressed during H-Street RED phase
- Verify GPIO pins (V: 9 & 10, H: 8 & 11) are correctly wired
- Test LEDs individually with `test_leds.py`

## Future Enhancements

Possible additions:
- 🔘 Physical buttons instead of keyboard keys
- 🔊 Audio signal for visually impaired pedestrians
- ⏱️ Countdown timer display
- � Pedestrian crossing statistics logging
- � School zone mode with extended crossing times

## Component Summary

### Total Components:
- 10 LEDs total:
  - 6 for traffic lights (3 per street)
  - 4 for pedestrian signals (2 per crossing)
- 10 Resistors (220Ω each)
- 1 Breadboard
- Jumper wires
- Raspberry Pi

### Cost Estimate:
- Additional LEDs (4): ~$2-4
- Additional Resistors (2): ~$0.50
- **Total additional cost for dual pedestrian feature: ~$3**

## Standards Compliance

This implementation follows real-world traffic signal standards:
- ✅ Pedestrian signals activate only during vehicle RED phase
- ✅ Minimum crossing time provided (9 seconds)
- ✅ Clear WALK/DON'T WALK indications
- ✅ Request queuing system
- ✅ Independent operation for each crossing direction

---

**Safety First!** 🚦🚶 The system ensures pedestrians only cross when the respective street's traffic is stopped.

## Key Controls Summary

| Key | Action | When Active |
|-----|--------|-------------|
| **O** | Request V-Street crossing | During V-Street RED phase |
| **P** | Request H-Street crossing | During H-Street RED phase |
| **Ctrl+C** | Emergency shutdown | Anytime |

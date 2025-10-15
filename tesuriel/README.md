# Traffic Control System for Raspberry Pi

## 🚦 Overview

A production-grade traffic light controller implementing a 4-state Finite State Machine (FSM) with safety invariants, designed for two-way intersection control on Raspberry Pi.

**Version:** 2.0 (Enhanced FSM)  
**Date:** October 15, 2025

---

## ✨ Key Features

### Core FSM Implementation
- **4-State Cycle:** `V_GREEN → V_YELLOW → H_GREEN → H_YELLOW` with ALL_RED clearance
- **Safety Invariant:** V_YELLOW ends exactly when H transitions from RED to GREEN
- **Configurable Timing:** 24-second base cycle (9s green, 3s yellow per direction)
- **ALL_RED Clearance:** 1-second buffer between transitions for safety

### Advanced Features
- ✅ **Pedestrian Crossing:** Direction-specific requests served during conflicting traffic RED
- ✅ **Emergency Preemption:** Flashing red override for emergency vehicles
- ✅ **Night Mode:** Blinking yellow lights on both directions (low-traffic hours)
- ✅ **Maintenance Mode:** All lights off for servicing
- ✅ **Mock GPIO:** Runs in simulation mode without Raspberry Pi hardware

---

## 📊 State Machine Design

### State Sequence

```
┌─────────────────────────────────────────────────────────────┐
│                    24-Second Cycle                           │
└─────────────────────────────────────────────────────────────┘

Time | State      | V-Street | H-Street | Duration
-----|------------|----------|----------|----------
0s   | V_GREEN    | 🟢 GREEN | 🔴 RED   | 9s
9s   | V_YELLOW   | 🟡 YELLOW| 🔴 RED   | 3s
12s  | ALL_RED    | 🔴 RED   | 🔴 RED   | 1s (clearance)
13s  | H_GREEN    | 🔴 RED   | 🟢 GREEN | 9s
22s  | H_YELLOW   | 🔴 RED   | 🟡 YELLOW| 3s
25s  | ALL_RED    | 🔴 RED   | 🔴 RED   | 1s (clearance)
26s  | [CYCLE REPEATS]
```

### Critical Invariant

**"When V-street yellow ends, H-street red ends. Therefore, as V goes into Red, H goes into Green."**

This is enforced by:
1. V_YELLOW duration (3s) + ALL_RED (1s) = precise timing before H_GREEN
2. No overlap of green lights (prevents collisions)
3. ALL_RED clearance prevents late-yellow runners from colliding with early-green starters

---

## 🔌 Hardware Setup

### GPIO Pin Configuration

#### V-Street (Vertical)
- **Red LED:** GPIO 17
- **Yellow LED:** GPIO 27
- **Green LED:** GPIO 22

#### H-Street (Horizontal)
- **Red LED:** GPIO 5
- **Yellow LED:** GPIO 6
- **Green LED:** GPIO 13

#### Control Buttons
- **Pedestrian V-Street Button:** GPIO 23 (crosses V during H_GREEN)
- **Pedestrian H-Street Button:** GPIO 24 (crosses H during V_GREEN)
- **Emergency Override:** GPIO 25

### Wiring Diagram

```
┌─────────────────────────────────────┐
│        Raspberry Pi                 │
│                                     │
│  GPIO 17 ──[220Ω]───(V Red LED)    │
│  GPIO 27 ──[220Ω]───(V Yellow LED) │
│  GPIO 22 ──[220Ω]───(V Green LED)  │
│                                     │
│  GPIO 5  ──[220Ω]───(H Red LED)    │
│  GPIO 6  ──[220Ω]───(H Yellow LED) │
│  GPIO 13 ──[220Ω]───(H Green LED)  │
│                                     │
│  GPIO 23 ──[Button]──┬─[10kΩ]─3.3V │
│  GPIO 24 ──[Button]──┤             │
│  GPIO 25 ──[Button]──┘             │
│                                     │
│  GND ─────────────────── (Common)  │
└─────────────────────────────────────┘

All LEDs: 220Ω current-limiting resistors
Buttons: 10kΩ pull-up (internal pull-up used in code)
```

### Component List

| Component | Quantity | Notes |
|-----------|----------|-------|
| Raspberry Pi (any model with GPIO) | 1 | Tested on Pi 3B+, 4 |
| Red LEDs | 2 | 5mm, standard brightness |
| Yellow LEDs | 2 | 5mm, standard brightness |
| Green LEDs | 2 | 5mm, standard brightness |
| 220Ω Resistors | 6 | Current limiting for LEDs |
| Tactile Push Buttons | 3 | Normally open |
| Breadboard | 1 | Standard size |
| Jumper Wires | ~20 | Male-to-female recommended |

---

## 🚀 Installation & Setup

### Prerequisites

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade

# Install Python 3 (usually pre-installed)
sudo apt-get install python3 python3-pip

# Install RPi.GPIO library
pip3 install RPi.GPIO
```

### Installation

```bash
# Clone or download main.py to your Raspberry Pi
cd ~
mkdir traffic-control
cd traffic-control
# Copy main.py here

# Make executable
chmod +x main.py

# Test in simulation mode (no hardware)
python3 main.py
```

### Running on Hardware

```bash
# Run with sudo (required for GPIO access)
sudo python3 main.py
```

---

## 💻 Usage

### Interactive Menu

Once started, you'll see an interactive menu:

```
Traffic Light Control Menu - 4-State FSM Controller
============================================================
1. Set NORMAL mode (4-state cycle)
2. Set NIGHT mode (blinking yellow both directions)
3. Set MAINTENANCE mode (all off)
4. Trigger EMERGENCY override (flashing red)
5. Request pedestrian crossing V-street (during H green)
6. Request pedestrian crossing H-street (during V green)
7. Show timing analysis
8. Exit
============================================================
```

### Operating Modes

#### 1. NORMAL Mode (Default)
- Runs the full 4-state FSM cycle
- Handles pedestrian requests automatically
- Standard operation for active intersection

#### 2. NIGHT Mode
- Blinking yellow on both V and H streets
- Used during low-traffic hours (e.g., 10 PM - 6 AM)
- Drivers treat as yield/caution

#### 3. MAINTENANCE Mode
- All lights off
- Used when servicing the intersection
- Manual traffic control required

#### 4. EMERGENCY Mode
- Flashing red on both directions
- All traffic must stop
- Triggered by emergency button or menu option

---

## 🚶 Pedestrian Crossing Logic

### Safety Rules

1. **V-Street Crossing:** Only served during `H_GREEN` state (V is red, safe to cross V)
2. **H-Street Crossing:** Only served during `V_GREEN` state (H is red, safe to cross H)
3. **No interruption:** Pedestrian requests extend the current green phase, don't interrupt it
4. **Walk Time:** 8 seconds for crossing
5. **Clearance:** 2 seconds "Don't Walk" flashing before transition

### Example Scenario

```
User presses "Pedestrian V-Street Button" at t=15s

Timeline:
15s - Request registered (system is in H_GREEN)
15s - WALK signal immediately (H stays green, V stays red)
15-23s - Pedestrian crossing time (8s)
23-25s - DON'T WALK clearance (2s)
25s - H_YELLOW proceeds as normal
```

---

## 🔍 Edge Cases Handled

### 1. Race Conditions / Timer Jitter
- **Problem:** CPU load could delay state transitions
- **Solution:** Using monotonic time checks with 0.1s polling intervals

### 2. Multiple Pedestrian Requests
- **Problem:** Button pressed multiple times
- **Solution:** Requests coalesced into single pending flag (debounced)

### 3. Pedestrian During Yellow
- **Problem:** Button pressed during yellow phase
- **Solution:** Request queued, served at next appropriate green phase

### 4. Emergency During Pedestrian Crossing
- **Problem:** Emergency vehicle while pedestrians crossing
- **Solution:** Emergency override immediately activates (pedestrians should stop)

### 5. Mode Change Mid-Cycle
- **Problem:** User changes mode during state execution
- **Solution:** Current state completes, new mode takes effect on next iteration

---

## 📈 Timing Analysis

### Verification Checklist

- ✅ **Timer durations sum to cycle length:** 9 + 3 + 1 + 9 + 3 + 1 = 26 seconds
- ✅ **State transitions align V_YELLOW end to H_RED end:** ALL_RED buffer ensures safe transition
- ✅ **Pedestrians scheduled only during conflicting traffic RED:** Logic enforced in `can_serve_pedestrian_*()` methods
- ✅ **ALL_RED clearance:** 1 second buffer prevents collisions from late-yellow runners

### Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Cycle Duration | 26s | Including clearances |
| Throughput (V) | 12s green+yellow per 26s | 46% duty cycle |
| Throughput (H) | 12s green+yellow per 26s | 46% duty cycle |
| Safety Buffer | 1s all-red per transition | Industry standard 0.5-2s |
| Pedestrian Wait (max) | 26s | Worst case: request just missed |
| Pedestrian Walk | 8s | Configurable |

---

## 🛠️ Configuration

### Adjustable Parameters (in `main.py`)

```python
# State durations
V_GREEN_TIME = 9
V_YELLOW_TIME = 3
H_GREEN_TIME = 9
H_YELLOW_TIME = 3

# Safety settings
ALL_RED_CLEARANCE = 1.0
PEDESTRIAN_WALK_TIME = 8
PEDESTRIAN_CLEARANCE = 2

# Night mode
NIGHT_MODE_YELLOW_BLINK_INTERVAL = 1
```

### Recommended Settings by Intersection Type

| Intersection Type | V_GREEN | H_GREEN | ALL_RED | Notes |
|-------------------|---------|---------|---------|-------|
| Low Traffic | 7s | 7s | 1s | Balanced, quick cycles |
| Arterial Road (V) | 12s | 6s | 1.5s | Favor main road |
| Residential | 9s | 9s | 1s | Equal priority (default) |
| High Pedestrian | 12s | 12s | 2s | Longer greens, safer clearance |

---

## 🧪 Testing Without Hardware

The system includes mock GPIO for testing on any computer:

```bash
# Run on Windows, Mac, or Linux (no Pi required)
python main.py

# Output shows simulated LED states:
[MOCK] GPIO setup: pin 17, mode OUT
[MOCK] RED LED: ON
[MOCK] YELLOW LED: OFF
...
```

This allows full algorithm testing before deploying to Raspberry Pi hardware.

---

## 🐛 Troubleshooting

### Common Issues

#### 1. `ImportError: No module named RPi.GPIO`
**Solution:** 
```bash
pip3 install RPi.GPIO
# OR run in simulation mode (mock GPIO automatically loads)
```

#### 2. `RuntimeError: No access to /dev/mem`
**Solution:** Run with sudo:
```bash
sudo python3 main.py
```

#### 3. LEDs don't light up
**Check:**
- Correct GPIO pin numbers in code match your wiring
- 220Ω resistors installed for each LED
- LEDs connected with correct polarity (long leg = anode = +)
- Ground connection from Pi to breadboard

#### 4. Buttons not responding
**Check:**
- Button pins match code configuration
- Internal pull-up configured in code (already done)
- Button wiring: one side to GPIO, other to GND

---

## 📚 Further Enhancements

### Potential Additions

1. **Multi-Intersection Coordination**
   - Network multiple controllers
   - Green wave synchronization for arterial roads

2. **Adaptive Timing**
   - Sensors to detect traffic volume
   - Dynamic green time allocation

3. **Web Interface**
   - Remote monitoring via Flask/FastAPI
   - Real-time status display
   - Remote mode switching

4. **Logging & Analytics**
   - State transition logging
   - Pedestrian request statistics
   - Maintenance alert system

5. **Hardware Enhancements**
   - 7-segment countdown timers
   - Pedestrian walk/don't walk indicators
   - Sound beepers for visually impaired

---

## 📄 License

MIT License - Feel free to use, modify, and distribute.

---

## 👨‍💻 Author

Traffic Control System v2.0  
Implemented: October 15, 2025  
Raspberry Pi GPIO-based FSM controller

---

## 🙏 Acknowledgments

- FSM design based on standard traffic engineering principles
- Safety invariants derived from DOT intersection standards
- Raspberry Pi GPIO library by Ben Croston

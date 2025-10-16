# Development Guide

## Running on Windows (Simulation Mode)

The traffic control system now supports **simulation mode** for development and testing on Windows or any non-Raspberry Pi system!

### How It Works

The code automatically detects if it's running on a Raspberry Pi:
- ✅ **On Raspberry Pi**: Uses real `RPi.GPIO` library to control actual LEDs
- ⚠️ **On Windows/Mac/Linux**: Uses mock GPIO to simulate the behavior

### Running in Simulation Mode

```powershell
# Just run the script normally on Windows
python main.py
```

You'll see output like:
```
⚠ RPi.GPIO not available - Running in SIMULATION mode
[MOCK] GPIO.output(pin=17, state=HIGH)
[13:10:49] V-Street (Vertical): RED
```

### Stopping the Simulation

Press `Ctrl + C` to stop the program safely.

### What You'll See

The simulation shows:
- All GPIO operations (setup, output changes)
- Traffic light state changes with timestamps
- Phase transitions (H-Street Active → V-Street Active)
- Cycle counts

### Testing Before Deployment

1. **Test on Windows**: Run `python main.py` to verify logic and timing
2. **Check timing**: Verify Red (12s), Green (9s), Yellow (3s) cycles
3. **Deploy to Raspberry Pi**: Copy files and run with actual hardware
4. **Test LEDs**: Use `python test_leds.py` on Raspberry Pi to verify wiring

## Deploying to Raspberry Pi

### 1. Transfer Files

```bash
# Option A: Use SCP (from Windows)
scp main.py pi@raspberrypi.local:~/robotics-mini-project/

# Option B: Use Git
git clone <your-repo> ~/robotics-mini-project

# Option C: Manual copy via USB drive
```

### 2. Install Dependencies

```bash
# On Raspberry Pi
sudo apt-get update
sudo apt-get install python3-rpi.gpio -y
```

### 3. Run on Raspberry Pi

```bash
cd ~/robotics-mini-project
sudo python3 main.py
```

The system will automatically detect the Raspberry Pi and use real GPIO!

## Quick Start Checklist

### Development Phase (Windows)
- [ ] Write and test code logic in simulation mode
- [ ] Verify timing sequences
- [ ] Check error handling
- [ ] Test startup/shutdown sequences

### Deployment Phase (Raspberry Pi)
- [ ] Wire LEDs according to `circuit_diagram.txt`
- [ ] Test individual LEDs with `test_leds.py`
- [ ] Run `main.py` with sudo
- [ ] Verify all traffic light phases work correctly
- [ ] Test emergency shutdown (Ctrl+C)

## Advantages of Simulation Mode

✅ Develop without Raspberry Pi hardware  
✅ Test logic and timing on any computer  
✅ Debug without risk of hardware damage  
✅ Faster development cycle  
✅ Same code works everywhere  

## Troubleshooting

### On Windows
- **Error**: `python: command not found`
  - **Fix**: Use `python3` or check Python installation
  
### On Raspberry Pi
- **Error**: `Permission denied`
  - **Fix**: Run with `sudo python3 main.py`

- **Error**: `No module named RPi.GPIO`
  - **Fix**: Install with `sudo apt-get install python3-rpi.gpio`

- **LEDs not working**
  - **Fix**: Check wiring, run `test_leds.py` to diagnose

## Code Structure

```
main.py
├── GPIO Detection (auto-selects real or mock)
├── TrafficLight class (controls individual light)
├── TrafficControlSystem class (manages intersection)
│   ├── startup_sequence()
│   ├── run_cycle()
│   └── shutdown()
└── main() - entry point
```

## Next Steps

1. ✅ Test simulation on Windows
2. ⏩ Build circuit on breadboard  
3. ⏩ Test with `test_leds.py`
4. ⏩ Run full system on Raspberry Pi
5. ⏩ Adjust timing if needed

Happy coding! 🚦

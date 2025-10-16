"""
Traffic Control System for Road Intersection
Raspberry Pi Implementation

Streets:
- V (Vertical): 2-lane street
- H (Horizontal): 2-lane street

Traffic Light Timing:
- Red: 12 seconds
- Green: 9 seconds
- Yellow: 3 seconds
Total cycle: 24 seconds per direction
"""

import time
from datetime import datetime

# Try to import RPi.GPIO for Raspberry Pi, otherwise use mock for development
try:
    import RPi.GPIO as GPIO
    SIMULATION_MODE = False
    print("✓ Running on Raspberry Pi - Real GPIO mode")
except (ImportError, RuntimeError):
    # Mock GPIO for development on non-Raspberry Pi systems
    print("⚠ RPi.GPIO not available - Running in SIMULATION mode")
    SIMULATION_MODE = True
    
    class MockGPIO:
        """Mock GPIO class for testing on non-Raspberry Pi systems"""
        BCM = "BCM"
        OUT = "OUT"
        LOW = 0
        HIGH = 1
        
        _pin_states = {}
        
        @staticmethod
        def setmode(mode):
            print(f"[MOCK] GPIO.setmode({mode})")
        
        @staticmethod
        def setwarnings(flag):
            print(f"[MOCK] GPIO.setwarnings({flag})")
        
        @staticmethod
        def setup(pin, mode, initial=None):
            MockGPIO._pin_states[pin] = initial if initial is not None else MockGPIO.LOW
            print(f"[MOCK] GPIO.setup(pin={pin}, mode={mode}, initial={initial})")
        
        @staticmethod
        def output(pin, state):
            MockGPIO._pin_states[pin] = state
            state_str = "HIGH" if state == MockGPIO.HIGH else "LOW"
            print(f"[MOCK] GPIO.output(pin={pin}, state={state_str})")
        
        @staticmethod
        def cleanup():
            print(f"[MOCK] GPIO.cleanup() - Cleaned up {len(MockGPIO._pin_states)} pins")
            MockGPIO._pin_states.clear()
    
    GPIO = MockGPIO()

# GPIO Pin Configuration
# Vertical Street (V) Traffic Lights
V_RED_PIN = 17
V_YELLOW_PIN = 27
V_GREEN_PIN = 22

# Horizontal Street (H) Traffic Lights
H_RED_PIN = 23
H_YELLOW_PIN = 24
H_GREEN_PIN = 25

# Timing Configuration (in seconds)
RED_TIME = 12
GREEN_TIME = 9
YELLOW_TIME = 3

class TrafficLight:
    """Class to represent a traffic light with three colors"""
    
    def __init__(self, red_pin, yellow_pin, green_pin, name):
        self.red_pin = red_pin
        self.yellow_pin = yellow_pin
        self.green_pin = green_pin
        self.name = name
        
        # Setup GPIO pins
        GPIO.setup(self.red_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.yellow_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.green_pin, GPIO.OUT, initial=GPIO.LOW)
    
    def red_on(self):
        """Turn on red light, turn off others"""
        GPIO.output(self.red_pin, GPIO.HIGH)
        GPIO.output(self.yellow_pin, GPIO.LOW)
        GPIO.output(self.green_pin, GPIO.LOW)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.name}: RED 🔴")
    
    def yellow_on(self):
        """Turn on yellow light, turn off others"""
        GPIO.output(self.red_pin, GPIO.LOW)
        GPIO.output(self.yellow_pin, GPIO.HIGH)
        GPIO.output(self.green_pin, GPIO.LOW)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.name}: YELLOW 🟡")
    
    def green_on(self):
        """Turn on green light, turn off others"""
        GPIO.output(self.red_pin, GPIO.LOW)
        GPIO.output(self.yellow_pin, GPIO.LOW)
        GPIO.output(self.green_pin, GPIO.HIGH)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.name}: GREEN 🟢")
    
    def all_off(self):
        """Turn off all lights"""
        GPIO.output(self.red_pin, GPIO.LOW)
        GPIO.output(self.yellow_pin, GPIO.LOW)
        GPIO.output(self.green_pin, GPIO.LOW)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.name}: ALL OFF ⚫")


class TrafficControlSystem:
    """Main traffic control system managing the intersection"""
    
    def __init__(self):
        # Setup GPIO mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Initialize traffic lights for both streets
        self.v_street = TrafficLight(V_RED_PIN, V_YELLOW_PIN, V_GREEN_PIN, "V-Street (Vertical)")
        self.h_street = TrafficLight(H_RED_PIN, H_YELLOW_PIN, H_GREEN_PIN, "H-Street (Horizontal)")
        
        print("="*60)
        print("Traffic Control System Initialized")
        print("="*60)
        if SIMULATION_MODE:
            print("⚠ RUNNING IN SIMULATION MODE - No actual GPIO control")
        print(f"Vertical Street (V) - Red: GPIO{V_RED_PIN}, Yellow: GPIO{V_YELLOW_PIN}, Green: GPIO{V_GREEN_PIN}")
        print(f"Horizontal Street (H) - Red: GPIO{H_RED_PIN}, Yellow: GPIO{H_YELLOW_PIN}, Green: GPIO{H_GREEN_PIN}")
        print(f"Timing: Red={RED_TIME}s, Green={GREEN_TIME}s, Yellow={YELLOW_TIME}s")
        print("="*60)
    
    def startup_sequence(self):
        """Initial startup sequence - flash all lights"""
        print("\n>>> Starting up system...")
        for _ in range(3):
            self.v_street.yellow_on()
            self.h_street.yellow_on()
            time.sleep(0.5)
            self.v_street.all_off()
            self.h_street.all_off()
            time.sleep(0.5)
        print(">>> System ready!\n")
    
    def run_cycle(self):
        """
        Run one complete traffic light cycle - SAFE MODE
        
        Cycle sequence (prevents green light collisions):
        1. V-Street: RED (12s)    | H-Street: GREEN (9s) → YELLOW (3s) → RED
        2. V-Street: GREEN (9s) → YELLOW (3s) → RED | H-Street: RED (12s)
        
        Both streets are NEVER green at the same time - one must be RED
        while the other goes through GREEN → YELLOW sequence.
        """
        
        # Phase 1: H-Street Active, V-Street STAYS RED throughout
        print("\n--- PHASE 1: H-Street Active (V-Street 🔴 RED) ---")
        self.v_street.red_on()
        self.h_street.green_on()
        time.sleep(GREEN_TIME)
        
        # H-Street transitions to yellow (V-Street STILL RED)
        print("    H-Street: GREEN 🟢 → YELLOW 🟡")
        self.h_street.yellow_on()
        time.sleep(YELLOW_TIME)
        
        # H-Street turns RED before V-Street gets green (SAFETY CRITICAL)
        print("    H-Street: YELLOW 🟡 → RED 🔴")
        self.h_street.red_on()
        time.sleep(1)  # 1 second safety buffer with both RED
        
        # Phase 2: V-Street Active, H-Street STAYS RED throughout
        print("\n--- PHASE 2: V-Street Active (H-Street 🔴 RED) ---")
        self.v_street.green_on()
        time.sleep(GREEN_TIME)
        
        # V-Street transitions to yellow (H-Street STILL RED)
        print("    V-Street: GREEN 🟢 → YELLOW 🟡")
        self.v_street.yellow_on()
        time.sleep(YELLOW_TIME)
        
        # V-Street turns RED before next cycle (SAFETY CRITICAL)
        print("    V-Street: YELLOW 🟡 → RED 🔴")
        self.v_street.red_on()
        time.sleep(1)  # 1 second safety buffer with both RED
    
    def run(self):
        """Main run loop - continuously cycle through traffic light phases"""
        try:
            self.startup_sequence()
            
            cycle_count = 0
            while True:
                cycle_count += 1
                print(f"\n{'='*60}")
                print(f"CYCLE {cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*60}")
                
                self.run_cycle()
                
        except KeyboardInterrupt:
            print("\n\n>>> Traffic Control System shutting down...")
            self.shutdown()
    
    def shutdown(self):
        """Safely shutdown the system"""
        # Turn all lights to red for safety
        self.v_street.red_on()
        self.h_street.red_on()
        time.sleep(2)
        
        # Turn off all lights
        self.v_street.all_off()
        self.h_street.all_off()
        
        # Cleanup GPIO
        GPIO.cleanup()
        print(">>> System shutdown complete. GPIO cleaned up.")


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("RASPBERRY PI TRAFFIC CONTROL SYSTEM")
    print("2-Lane Intersection: V-Street (Vertical) & H-Street (Horizontal)")
    print("="*60 + "\n")
    
    # Create and run the traffic control system
    traffic_system = TrafficControlSystem()
    traffic_system.run()


if __name__ == "__main__":
    main()

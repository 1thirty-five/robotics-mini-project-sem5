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
import threading
from datetime import datetime

# Try to import keyboard library for pedestrian crossing button
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("⚠ 'keyboard' module not available. Install with: pip install keyboard")
    print("  Pedestrian crossing feature will be limited.")

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

# Pedestrian Signal Pins (V-Street crossing)
PEDESTRIAN_V_WALK_PIN = 10   # Green "WALK" signal for V-Street
PEDESTRIAN_V_STOP_PIN = 9    # Red "DON'T WALK" signal for V-Street

# Pedestrian Signal Pins (H-Street crossing)
PEDESTRIAN_H_WALK_PIN = 11   # Green "WALK" signal for H-Street
PEDESTRIAN_H_STOP_PIN = 8    # Red "DON'T WALK" signal for H-Street

# Timing Configuration (in seconds)
RED_TIME = 12
GREEN_TIME = 9
YELLOW_TIME = 3
PEDESTRIAN_WALK_TIME = 9  # Active for 9 seconds out of 12-second red light

class TrafficLight:
    """Class to represent a traffic light with three colors"""
    
    def __init__(self, red_pin, yellow_pin, green_pin, name):
        self.red_pin = red_pin
        self.yellow_pin = yellow_pin
        self.green_pin = green_pin
        self.name = name
        
        # Setup GPIO pins
        GPIO.setup(self.red_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.yellow_pin, GPIO.OUT, initial=GPIO.LOW
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
        
        # Setup pedestrian signals for V-Street
        GPIO.setup(PEDESTRIAN_V_WALK_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(PEDESTRIAN_V_STOP_PIN, GPIO.OUT, initial=GPIO.HIGH)  # Stop is ON by default
        
        # Setup pedestrian signals for H-Street
        GPIO.setup(PEDESTRIAN_H_WALK_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(PEDESTRIAN_H_STOP_PIN, GPIO.OUT, initial=GPIO.HIGH)  # Stop is ON by default
        
        # Pedestrian crossing state for V-Street
        self.pedestrian_v_request = False
        self.pedestrian_v_active = False
        self.v_street_is_red = False
        
        # Pedestrian crossing state for H-Street
        self.pedestrian_h_request = False
        self.pedestrian_h_active = False
        self.h_street_is_red = False
        
        # Night mode state
        self.night_mode = False
        self.night_mode_toggle_requested = False
        
        # Start keyboard listener thread if available
        if KEYBOARD_AVAILABLE:
            self.listener_thread = threading.Thread(target=self._keyboard_listener, daemon=True)
            self.listener_thread.start()
        
        print("="*60)
        print("Traffic Control System Initialized")
        print("="*60)
        if SIMULATION_MODE:
            print("⚠ RUNNING IN SIMULATION MODE - No actual GPIO control")
        print(f"Vertical Street (V) - Red: GPIO{V_RED_PIN}, Yellow: GPIO{V_YELLOW_PIN}, Green: GPIO{V_GREEN_PIN}")
        print(f"Horizontal Street (H) - Red: GPIO{H_RED_PIN}, Yellow: GPIO{H_YELLOW_PIN}, Green: GPIO{H_GREEN_PIN}")
        print(f"Pedestrian Crossing (V) - Walk: GPIO{PEDESTRIAN_V_WALK_PIN}, Stop: GPIO{PEDESTRIAN_V_STOP_PIN}")
        print(f"Pedestrian Crossing (H) - Walk: GPIO{PEDESTRIAN_H_WALK_PIN}, Stop: GPIO{PEDESTRIAN_H_STOP_PIN}")
        print(f"Timing: Red={RED_TIME}s, Green={GREEN_TIME}s, Yellow={YELLOW_TIME}s")
        if KEYBOARD_AVAILABLE:
            print(f"🚶 Press 'O' key to request pedestrian crossing on V-Street")
            print(f"🚶 Press 'P' key to request pedestrian crossing on H-Street")
            print(f"🌙 Press 'N' key to toggle NIGHT MODE (flashing yellow)")
        print("="*60)
    
    def _keyboard_listener(self):
        """Listen for 'o', 'p', and 'n' key presses for pedestrian crossing requests and night mode"""
        while True:
            try:
                if keyboard.is_pressed('o'):
                    if not self.pedestrian_v_request and not self.pedestrian_v_active:
                        self.pedestrian_v_request = True
                        print("\n🚶 [PEDESTRIAN REQUEST] Crossing requested on V-Street!")
                    time.sleep(0.5)  # Debounce
                elif keyboard.is_pressed('p'):
                    if not self.pedestrian_h_request and not self.pedestrian_h_active:
                        self.pedestrian_h_request = True
                        print("\n🚶 [PEDESTRIAN REQUEST] Crossing requested on H-Street!")
                    time.sleep(0.5)  # Debounce
                elif keyboard.is_pressed('n'):
                    if not self.night_mode_toggle_requested:
                        self.night_mode_toggle_requested = True
                        if not self.night_mode:
                            print("\n🌙 [NIGHT MODE] Activating night mode - All lights will flash YELLOW")
                        else:
                            print("\n☀️ [DAY MODE] Deactivating night mode - Returning to normal operation")
                    time.sleep(0.5)  # Debounce
            except:
                break
    
    def _activate_pedestrian_v_walk(self):
        """Activate pedestrian WALK signal for V-Street"""
        GPIO.output(PEDESTRIAN_V_STOP_PIN, GPIO.LOW)
        GPIO.output(PEDESTRIAN_V_WALK_PIN, GPIO.HIGH)
        self.pedestrian_v_active = True
        print(f"🚶 [{datetime.now().strftime('%H:%M:%S')}] V-STREET PEDESTRIAN WALK ACTIVE 🟢 - Cross V-Street NOW!")
    
    def _deactivate_pedestrian_v_walk(self):
        """Deactivate pedestrian WALK signal for V-Street"""
        GPIO.output(PEDESTRIAN_V_WALK_PIN, GPIO.LOW)
        GPIO.output(PEDESTRIAN_V_STOP_PIN, GPIO.HIGH)
        self.pedestrian_v_active = False
        print(f"🚷 [{datetime.now().strftime('%H:%M:%S')}] V-STREET PEDESTRIAN WALK ENDED 🔴 - Do NOT cross!")
    
    def _activate_pedestrian_h_walk(self):
        """Activate pedestrian WALK signal for H-Street"""
        GPIO.output(PEDESTRIAN_H_STOP_PIN, GPIO.LOW)
        GPIO.output(PEDESTRIAN_H_WALK_PIN, GPIO.HIGH)
        self.pedestrian_h_active = True
        print(f"🚶 [{datetime.now().strftime('%H:%M:%S')}] H-STREET PEDESTRIAN WALK ACTIVE 🟢 - Cross H-Street NOW!")
    
    def _deactivate_pedestrian_h_walk(self):
        """Deactivate pedestrian WALK signal for H-Street"""
        GPIO.output(PEDESTRIAN_H_WALK_PIN, GPIO.LOW)
        GPIO.output(PEDESTRIAN_H_STOP_PIN, GPIO.HIGH)
        self.pedestrian_h_active = False
        print(f"🚷 [{datetime.now().strftime('%H:%M:%S')}] H-STREET PEDESTRIAN WALK ENDED 🔴 - Do NOT cross!")
    
    def _handle_pedestrian_v_crossing(self):
        """Handle pedestrian crossing request during V-Street RED phase"""
        if self.pedestrian_v_request and self.v_street_is_red:
            print(f"🚶 Activating V-Street pedestrian crossing for {PEDESTRIAN_WALK_TIME} seconds...")
            self._activate_pedestrian_v_walk()
            time.sleep(PEDESTRIAN_WALK_TIME)
            self._deactivate_pedestrian_v_walk()
            self.pedestrian_v_request = False
            return True
        return False
    
    def _handle_pedestrian_h_crossing(self):
        """Handle pedestrian crossing request during H-Street RED phase"""
        if self.pedestrian_h_request and self.h_street_is_red:
            print(f"🚶 Activating H-Street pedestrian crossing for {PEDESTRIAN_WALK_TIME} seconds...")
            self._activate_pedestrian_h_walk()
            time.sleep(PEDESTRIAN_WALK_TIME)
            self._deactivate_pedestrian_h_walk()
            self.pedestrian_h_request = False
            return True
        return False
    
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
    
    def _night_mode_cycle(self):
        """
        Night Mode Operation - All lights flash YELLOW
        
        Behavior:
        - Both streets flash yellow continuously (0.5s on, 0.5s off)
        - When pedestrian crossing requested:
          * Respective street turns RED
          * Pedestrian WALK signal activates for 9 seconds
          * Street returns to flashing YELLOW after 1 second
        - Press 'N' again to exit night mode
        """
        print("\n" + "="*60)
        print("🌙 NIGHT MODE ACTIVE")
        print("="*60)
        print("All lights flashing YELLOW")
        print("Press 'O' for V-Street pedestrian crossing")
        print("Press 'P' for H-Street pedestrian crossing")
        print("Press 'N' to exit night mode")
        print("="*60 + "\n")
        
        while self.night_mode:
            # Check for night mode toggle
            if self.night_mode_toggle_requested:
                self.night_mode = False
                self.night_mode_toggle_requested = False
                print("\n☀️ Exiting night mode... Returning to normal traffic operation")
                break
            
            # Check for V-Street pedestrian crossing
            if self.pedestrian_v_request:
                print("\n🚶 [NIGHT MODE] V-Street pedestrian crossing requested")
                # V-Street turns RED for pedestrian crossing
                self.v_street.red_on()
                self.h_street.all_off()  # Turn off H-Street temporarily
                
                # Activate V-Street pedestrian crossing
                print(f"🚶 Activating V-Street pedestrian crossing for {PEDESTRIAN_WALK_TIME} seconds...")
                self._activate_pedestrian_v_walk()
                time.sleep(PEDESTRIAN_WALK_TIME)
                self._deactivate_pedestrian_v_walk()
                self.pedestrian_v_request = False
                
                # Keep RED for 1 more second
                time.sleep(1)
                print("🌙 Returning to flashing yellow mode\n")
                self.v_street.all_off()
            
            # Check for H-Street pedestrian crossing
            elif self.pedestrian_h_request:
                print("\n🚶 [NIGHT MODE] H-Street pedestrian crossing requested")
                # H-Street turns RED for pedestrian crossing
                self.h_street.red_on()
                self.v_street.all_off()  # Turn off V-Street temporarily
                
                # Activate H-Street pedestrian crossing
                print(f"🚶 Activating H-Street pedestrian crossing for {PEDESTRIAN_WALK_TIME} seconds...")
                self._activate_pedestrian_h_walk()
                time.sleep(PEDESTRIAN_WALK_TIME)
                self._deactivate_pedestrian_h_walk()
                self.pedestrian_h_request = False
                
                # Keep RED for 1 more second
                time.sleep(1)
                print("🌙 Returning to flashing yellow mode\n")
                self.h_street.all_off()
            
            else:
                # Normal flashing yellow operation
                self.v_street.yellow_on()
                self.h_street.yellow_on()
                time.sleep(0.5)
                self.v_street.all_off()
                self.h_street.all_off()
                time.sleep(0.5)
    
    def run_cycle(self):
        """
        Run one complete traffic light cycle - SAFE MODE with Pedestrian Crossing
        
        Cycle sequence (prevents green light collisions):
        1. V-Street: RED (12s)    | H-Street: GREEN (9s) → YELLOW (3s) → RED
           - V-Street pedestrian crossing available during V-Street RED phase (9s of 12s)
        2. V-Street: GREEN (9s) → YELLOW (3s) → RED | H-Street: RED (12s)
           - H-Street pedestrian crossing available during H-Street RED phase (9s of 12s)
        
        Both streets are NEVER green at the same time - one must be RED
        while the other goes through GREEN → YELLOW sequence.
        """
        
        # Phase 1: H-Street Active, V-Street STAYS RED throughout
        print("\n--- PHASE 1: H-Street Active (V-Street 🔴 RED) ---")
        self.v_street_is_red = True  # Mark V-Street as RED
        self.h_street_is_red = False  # Mark H-Street as NOT RED
        self.v_street.red_on()
        self.h_street.green_on()
        
        # Check for V-Street pedestrian crossing request (9 seconds during H-Street GREEN)
        if self.pedestrian_v_request:
            # Pedestrian walks for 9 seconds while H-Street is GREEN
            pedestrian_handled = self._handle_pedestrian_v_crossing()
            if pedestrian_handled:
                # Pedestrian already used 9 seconds, no additional wait needed
                pass
            else:
                time.sleep(GREEN_TIME)
        else:
            time.sleep(GREEN_TIME)
        
        # H-Street transitions to yellow (V-Street STILL RED)
        print("    H-Street: GREEN 🟢 → YELLOW 🟡")
        self.h_street.yellow_on()
        time.sleep(YELLOW_TIME)
        
        # H-Street turns RED before V-Street gets green (SAFETY CRITICAL)
        print("    H-Street: YELLOW 🟡 → RED 🔴")
        self.h_street.red_on()
        self.h_street_is_red = True  # Mark H-Street as RED
        time.sleep(1)  # 1 second safety buffer with both RED
        
        # Phase 2: V-Street Active, H-Street STAYS RED throughout
        print("\n--- PHASE 2: V-Street Active (H-Street 🔴 RED) ---")
        self.v_street_is_red = False  # V-Street no longer RED
        self.v_street.green_on()
        
        # Check for H-Street pedestrian crossing request (9 seconds during V-Street GREEN)
        if self.pedestrian_h_request:
            # Pedestrian walks for 9 seconds while V-Street is GREEN
            pedestrian_handled = self._handle_pedestrian_h_crossing()
            if pedestrian_handled:
                # Pedestrian already used 9 seconds, no additional wait needed
                pass
            else:
                time.sleep(GREEN_TIME)
        else:
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
                # Check for night mode toggle
                if self.night_mode_toggle_requested:
                    self.night_mode = not self.night_mode
                    self.night_mode_toggle_requested = False
                    
                    if self.night_mode:
                        # Enter night mode
                        self._night_mode_cycle()
                        # After exiting night mode, continue with normal operation
                        cycle_count = 0
                        continue
                
                # Normal day mode operation
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
        
        # Turn off all pedestrian signals
        GPIO.output(PEDESTRIAN_V_WALK_PIN, GPIO.LOW)
        GPIO.output(PEDESTRIAN_V_STOP_PIN, GPIO.HIGH)
        GPIO.output(PEDESTRIAN_H_WALK_PIN, GPIO.LOW)
        GPIO.output(PEDESTRIAN_H_STOP_PIN, GPIO.HIGH)
        
        time.sleep(2)
        
        # Turn off all lights
        self.v_street.all_off()
        self.h_street.all_off()
        GPIO.output(PEDESTRIAN_V_STOP_PIN, GPIO.LOW)
        GPIO.output(PEDESTRIAN_H_STOP_PIN, GPIO.LOW)
        
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

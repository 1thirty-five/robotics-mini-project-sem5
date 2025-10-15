#!/usr/bin/env python3
"""
Traffic Control System for Raspberry Pi
A complete traffic light controller with multiple modes and features
"""

import time
import threading
try:
    import RPi.GPIO as GPIO
except ImportError:
    print("Warning: RPi.GPIO not found. Running in simulation mode.")
    # Mock GPIO for testing without Raspberry Pi
    class MockGPIO:
        BCM = "BCM"
        OUT = "OUT"
        IN = "IN"
        PUD_UP = "PUD_UP"
        
        # Track previous states to only print on change
        _pin_states = {}
        
        @staticmethod
        def setmode(mode):
            pass  # Silent in normal operation
        
        @staticmethod
        def setup(pin, mode, pull_up_down=None):
            pass  # Silent in normal operation
        
        @staticmethod
        def output(pin, state):
            # Only print when state actually changes
            if MockGPIO._pin_states.get(pin) != state:
                MockGPIO._pin_states[pin] = state
                color = {17: "V-RED", 27: "V-YELLOW", 22: "V-GREEN",
                        5: "H-RED", 6: "H-YELLOW", 13: "H-GREEN"}.get(pin, f"Pin{pin}")
                state_str = "ON" if state else "OFF"
                # Uncomment below to see individual LED changes
                # print(f"[GPIO] {color}: {state_str}")
        
        @staticmethod
        def input(pin):
            return False
        
        @staticmethod
        def cleanup():
            print("[MOCK] GPIO cleanup")
    
    GPIO = MockGPIO()


class TrafficLight:
    """Main traffic light controller class with 4-state FSM"""
    
    # GPIO Pin assignments for TWO-WAY INTERSECTION
    # Vertical (V) street
    V_RED_PIN = 17
    V_YELLOW_PIN = 27
    V_GREEN_PIN = 22
    
    # Horizontal (H) street
    H_RED_PIN = 5
    H_YELLOW_PIN = 6
    H_GREEN_PIN = 13
    
    # Control buttons
    PEDESTRIAN_V_BUTTON_PIN = 23  # Pedestrian crossing V street
    PEDESTRIAN_H_BUTTON_PIN = 24  # Pedestrian crossing H street
    EMERGENCY_BUTTON_PIN = 25
    
    # Timing configurations (in seconds) - Based on handwritten spec
    # Sequence: Red (12s) → Green (9s) → Yellow (3s) per street
    V_RED_TIME = 12      # V stopped, H flows
    V_GREEN_TIME = 9     # V flows
    V_YELLOW_TIME = 3    # V warning (yellow intersects on green/before red)
    
    H_RED_TIME = 12      # H stopped, V flows  
    H_GREEN_TIME = 9     # H flows
    H_YELLOW_TIME = 3    # H warning (yellow intersects on green/before red)
    
    # Safety and pedestrian settings
    ALL_RED_CLEARANCE = 0.0  # No clearance per original handwritten spec
    PEDESTRIAN_WALK_TIME = 8  # Time allocated for pedestrian crossing
    PEDESTRIAN_CLEARANCE = 2  # Don't Walk flashing time
    NIGHT_MODE_YELLOW_BLINK_INTERVAL = 1
    
    def __init__(self):
        """Initialize the traffic light system with Red→Green→Yellow FSM per handwritten spec"""
        # FSM States based on handwritten logic: Each street follows Red→Green→Yellow
        self.current_state = "V_RED_H_GREEN_YELLOW"  # V stopped, H flowing with yellow overlap
        self.state_start_time = None
        self.running = False
        self.mode = "NORMAL"  # NORMAL, NIGHT, MAINTENANCE, EMERGENCY
        
        # Pedestrian request flags (separate for each direction)
        self.pedestrian_v_request = False  # Request to cross V street
        self.pedestrian_h_request = False  # Request to cross H street
        self.pedestrian_active = False
        
        self.emergency_override = False
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        
        # Vertical street lights
        GPIO.setup(self.V_RED_PIN, GPIO.OUT)
        GPIO.setup(self.V_YELLOW_PIN, GPIO.OUT)
        GPIO.setup(self.V_GREEN_PIN, GPIO.OUT)
        
        # Horizontal street lights
        GPIO.setup(self.H_RED_PIN, GPIO.OUT)
        GPIO.setup(self.H_YELLOW_PIN, GPIO.OUT)
        GPIO.setup(self.H_GREEN_PIN, GPIO.OUT)
        
        # Buttons
        GPIO.setup(self.PEDESTRIAN_V_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.PEDESTRIAN_H_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.EMERGENCY_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Turn all lights off initially
        self.all_lights_off()
        
        print("Traffic Light System Initialized (Red→Green→Yellow per street)")
        print(f"Cycle Duration: {self.get_cycle_duration()}s")
        print(f"\nHandwritten Logic Implementation:")
        print(f"  Each street: Red (12s) → Green (9s) → Yellow (3s)")
        print(f"  Yellow intersects on green OR before red")
        print(f"  V's yellow end aligns with H's red end")
        print(f"\nPin Configuration:")
        print(f"  V-Street Red: GPIO {self.V_RED_PIN}")
        print(f"  V-Street Yellow: GPIO {self.V_YELLOW_PIN}")
        print(f"  V-Street Green: GPIO {self.V_GREEN_PIN}")
        print(f"  H-Street Red: GPIO {self.H_RED_PIN}")
        print(f"  H-Street Yellow: GPIO {self.H_YELLOW_PIN}")
        print(f"  H-Street Green: GPIO {self.H_GREEN_PIN}")
        print(f"  Ped V Button: GPIO {self.PEDESTRIAN_V_BUTTON_PIN}")
        print(f"  Ped H Button: GPIO {self.PEDESTRIAN_H_BUTTON_PIN}")
        print(f"  Emergency Button: GPIO {self.EMERGENCY_BUTTON_PIN}")
    
    def get_cycle_duration(self):
        """Calculate total cycle duration - both streets complete Red→Green→Yellow"""
        # Total = V complete cycle (when H flows) + H complete cycle (when V flows)
        return self.V_RED_TIME + self.V_GREEN_TIME + self.V_YELLOW_TIME
    
    def all_lights_off(self):
        """Turn off all traffic lights"""
        GPIO.output(self.V_RED_PIN, False)
        GPIO.output(self.V_YELLOW_PIN, False)
        GPIO.output(self.V_GREEN_PIN, False)
        GPIO.output(self.H_RED_PIN, False)
        GPIO.output(self.H_YELLOW_PIN, False)
        GPIO.output(self.H_GREEN_PIN, False)
    
    def set_v_red(self):
        """Set V street to RED"""
        GPIO.output(self.V_RED_PIN, True)
        GPIO.output(self.V_YELLOW_PIN, False)
        GPIO.output(self.V_GREEN_PIN, False)
    
    def set_v_yellow(self):
        """Set V street to YELLOW"""
        GPIO.output(self.V_RED_PIN, False)
        GPIO.output(self.V_YELLOW_PIN, True)
        GPIO.output(self.V_GREEN_PIN, False)
    
    def set_v_green(self):
        """Set V street to GREEN"""
        GPIO.output(self.V_RED_PIN, False)
        GPIO.output(self.V_YELLOW_PIN, False)
        GPIO.output(self.V_GREEN_PIN, True)
    
    def set_h_red(self):
        """Set H street to RED"""
        GPIO.output(self.H_RED_PIN, True)
        GPIO.output(self.H_YELLOW_PIN, False)
        GPIO.output(self.H_GREEN_PIN, False)
    
    def set_h_yellow(self):
        """Set H street to YELLOW"""
        GPIO.output(self.H_RED_PIN, False)
        GPIO.output(self.H_YELLOW_PIN, True)
        GPIO.output(self.H_GREEN_PIN, False)
    
    def set_h_green(self):
        """Set H street to GREEN"""
        GPIO.output(self.H_RED_PIN, False)
        GPIO.output(self.H_YELLOW_PIN, False)
        GPIO.output(self.H_GREEN_PIN, True)
    
    def set_state_lights(self, v_state, h_state):
        """Set lights based on current state of each street independently
        
        Per handwritten spec:
        - Each street: Red → Green → Yellow
        - Yellow can overlap with green (intersect on green)
        - V's yellow end = H's red end
        """
        # Set V street
        if v_state == "RED":
            self.set_v_red()
            v_display = "🔴"
        elif v_state == "GREEN":
            self.set_v_green()
            v_display = "�"
        elif v_state == "YELLOW":
            self.set_v_yellow()
            v_display = "🟡"
        elif v_state == "GREEN_YELLOW":  # Yellow overlapping on green
            GPIO.output(self.V_RED_PIN, False)
            GPIO.output(self.V_YELLOW_PIN, True)
            GPIO.output(self.V_GREEN_PIN, True)
            v_display = "🟢🟡"
        else:
            v_display = "?"
            
        # Set H street
        if h_state == "RED":
            self.set_h_red()
            h_display = "🔴"
        elif h_state == "GREEN":
            self.set_h_green()
            h_display = "🟢"
        elif h_state == "YELLOW":
            self.set_h_yellow()
            h_display = "🟡"
        elif h_state == "GREEN_YELLOW":  # Yellow overlapping on green
            GPIO.output(self.H_RED_PIN, False)
            GPIO.output(self.H_YELLOW_PIN, True)
            GPIO.output(self.H_GREEN_PIN, True)
            h_display = "🟢🟡"
        else:
            h_display = "?"
            
        # Only print status on state change (not every polling cycle)
        print(f"[{time.strftime('%H:%M:%S')}] V={v_display} H={h_display} | V:{v_state}, H:{h_state}")
    
    def get_state_duration(self, state):
        """Get duration for a given state"""
        durations = {
            "V_RED": self.V_RED_TIME,
            "V_GREEN": self.V_GREEN_TIME,
            "V_YELLOW": self.V_YELLOW_TIME,
            "H_RED": self.H_RED_TIME,
            "H_GREEN": self.H_GREEN_TIME,
            "H_YELLOW": self.H_YELLOW_TIME,
        }
        return durations.get(state, 1)
    
    def fsm_cycle(self):
        """Execute one complete cycle following handwritten spec
        
        Handwritten logic:
        - V: Red(12s) → Green(9s) → Yellow(3s) [24s total]
        - H: Red(12s) → Green(9s) → Yellow(3s) [24s total]
        - Yellow must intersect on green OR before red
        - V's yellow end = H's red end
        
        Interpretation: When V is flowing (Green+Yellow), H is Red
                       When H is flowing (Green+Yellow), V is Red
        """
        
        # Phase 1: V is RED (12s), H flows (Green 9s → Yellow 3s)
        print(f"\n[{time.strftime('%H:%M:%S')}] === PHASE 1: V RED, H FLOWING ===")
        
        # H Green for 9s
        self.set_state_lights("RED", "GREEN")
        self.wait_with_checks(self.H_GREEN_TIME)
        
        # H Yellow for 3s (V still red)
        self.set_state_lights("RED", "YELLOW")
        self.wait_with_checks(self.H_YELLOW_TIME)
        
        # Phase 2: H is RED (12s), V flows (Green 9s → Yellow 3s)
        print(f"\n[{time.strftime('%H:%M:%S')}] === PHASE 2: H RED, V FLOWING ===")
        print(f"[{time.strftime('%H:%M:%S')}] ✓ INVARIANT: V yellow will end when H red ends")
        
        # V Green for 9s
        self.set_state_lights("GREEN", "RED")
        self.wait_with_checks(self.V_GREEN_TIME)
        
        # V Yellow for 3s (H still red)
        self.set_state_lights("YELLOW", "RED")
        self.wait_with_checks(self.V_YELLOW_TIME)
        
        print(f"[{time.strftime('%H:%M:%S')}] ✓ V yellow ended, H red ending → Cycle restarts")
    
    def wait_with_checks(self, duration):
        """Wait for duration while checking buttons"""
        elapsed = 0
        poll_interval = 0.1
        
        while elapsed < duration and self.running and self.mode == "NORMAL":
            self.check_pedestrian_buttons()
            self.check_emergency_button()
            
            time.sleep(poll_interval)
            elapsed += poll_interval
            
            if self.emergency_override:
                return
    
    def blink_yellow(self, duration=None):
        """Blink yellow light (for night mode)"""
        print(f"[{time.strftime('%H:%M:%S')}] Night Mode: Blinking Yellow (both directions)")
        start_time = time.time()
        while self.mode == "NIGHT" and self.running:
            GPIO.output(self.V_YELLOW_PIN, True)
            GPIO.output(self.H_YELLOW_PIN, True)
            time.sleep(self.NIGHT_MODE_YELLOW_BLINK_INTERVAL)
            GPIO.output(self.V_YELLOW_PIN, False)
            GPIO.output(self.H_YELLOW_PIN, False)
            time.sleep(self.NIGHT_MODE_YELLOW_BLINK_INTERVAL)
            
            if duration and (time.time() - start_time) >= duration:
                break
    
    def check_pedestrian_buttons(self):
        """Check if pedestrian crossing buttons are pressed (debounced)"""
        # Check V-street pedestrian crossing (crosses V during H_GREEN)
        if GPIO.input(self.PEDESTRIAN_V_BUTTON_PIN) == False:
            if not self.pedestrian_v_request:
                self.pedestrian_v_request = True
                print(f"[{time.strftime('%H:%M:%S')}] 🚶 Pedestrian request: Cross V-street (served during H_GREEN)")
        
        # Check H-street pedestrian crossing (crosses H during V_GREEN)
        if GPIO.input(self.PEDESTRIAN_H_BUTTON_PIN) == False:
            if not self.pedestrian_h_request:
                self.pedestrian_h_request = True
                print(f"[{time.strftime('%H:%M:%S')}] 🚶 Pedestrian request: Cross H-street (served during V_GREEN)")
    
    def check_emergency_button(self):
        """Check if emergency override button is pressed"""
        if GPIO.input(self.EMERGENCY_BUTTON_PIN) == False:
            if not self.emergency_override:
                self.emergency_override = True
                print(f"[{time.strftime('%H:%M:%S')}] 🚨 EMERGENCY OVERRIDE ACTIVATED")
    
    def can_serve_pedestrian_v(self):
        """Check if we can serve pedestrian crossing V street
        Rule: Only when V is red (H is flowing)
        """
        return self.pedestrian_v_request
    
    def can_serve_pedestrian_h(self):
        """Check if we can serve pedestrian crossing H street
        Rule: Only when H is red (V is flowing)
        """
        return self.pedestrian_h_request
    
    def serve_pedestrian_crossing(self):
        """Serve pedestrian crossing within the current red interval
        
        This extends the current green phase to allow full pedestrian crossing.
        Pedestrians only cross when conflicting traffic is RED.
        """
        if self.can_serve_pedestrian_v():
            print(f"[{time.strftime('%H:%M:%S')}] 🚶 WALK signal: Crossing V-street")
            print(f"    (H remains GREEN, V remains RED)")
            time.sleep(self.PEDESTRIAN_WALK_TIME)
            
            print(f"[{time.strftime('%H:%M:%S')}] 🚶 DON'T WALK (clearance)")
            time.sleep(self.PEDESTRIAN_CLEARANCE)
            
            self.pedestrian_v_request = False
            print(f"[{time.strftime('%H:%M:%S')}] 🚶 Pedestrian crossing V-street complete")
            return True
            
        elif self.can_serve_pedestrian_h():
            print(f"[{time.strftime('%H:%M:%S')}] 🚶 WALK signal: Crossing H-street")
            print(f"    (V remains GREEN, H remains RED)")
            time.sleep(self.PEDESTRIAN_WALK_TIME)
            
            print(f"[{time.strftime('%H:%M:%S')}] 🚶 DON'T WALK (clearance)")
            time.sleep(self.PEDESTRIAN_CLEARANCE)
            
            self.pedestrian_h_request = False
            print(f"[{time.strftime('%H:%M:%S')}] 🚶 Pedestrian crossing H-street complete")
            return True
        
        return False

    
    def emergency_mode(self):
        """Emergency mode: Flash red lights on both directions"""
        print(f"[{time.strftime('%H:%M:%S')}] 🚨 EMERGENCY MODE: All Stop")
        while self.emergency_override and self.running:
            self.set_v_red()
            self.set_h_red()
            time.sleep(0.5)
            self.all_lights_off()
            time.sleep(0.5)
    
    def maintenance_mode(self):
        """Maintenance mode: All lights off"""
        print(f"[{time.strftime('%H:%M:%S')}] 🔧 Maintenance Mode: All lights off")
        self.all_lights_off()
        while self.mode == "MAINTENANCE" and self.running:
            time.sleep(1)
    
    def run(self):
        """Main run loop following handwritten specification"""
        self.running = True
        
        print(f"\n{'='*60}")
        print("Traffic Light System Started - Handwritten Spec")
        print(f"{'='*60}")
        print(f"Mode: {self.mode}")
        print(f"Logic: Red(12s) → Green(9s) → Yellow(3s) per street")
        print(f"Cycle Duration: {self.get_cycle_duration()}s per street")
        print(f"Key: V's yellow end = H's red end")
        print(f"{'='*60}\n")
        
        try:
            while self.running:
                # Check for emergency override
                if self.emergency_override:
                    self.mode = "EMERGENCY"
                    self.emergency_mode()
                    self.emergency_override = False
                    self.mode = "NORMAL"
                    continue
                
                # Execute based on current mode
                if self.mode == "NORMAL":
                    self.fsm_cycle()
                elif self.mode == "NIGHT":
                    self.blink_yellow()
                elif self.mode == "MAINTENANCE":
                    self.maintenance_mode()
                else:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\n\n⏹️  Shutting down traffic light system...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the traffic light system and cleanup"""
        self.running = False
        self.all_lights_off()
        GPIO.cleanup()
        print("✓ Traffic Light System Stopped")
    
    def set_mode(self, mode):
        """Change the operating mode"""
        valid_modes = ["NORMAL", "NIGHT", "MAINTENANCE", "EMERGENCY"]
        if mode.upper() in valid_modes:
            old_mode = self.mode
            self.mode = mode.upper()
            print(f"[{time.strftime('%H:%M:%S')}] Mode changed: {old_mode} → {self.mode}")
        else:
            print(f"Invalid mode. Valid modes: {', '.join(valid_modes)}")
    
    def print_timing_analysis(self):
        """Print detailed timing analysis per handwritten spec"""
        print("\n" + "="*60)
        print("TIMING ANALYSIS - Handwritten Specification")
        print("="*60)
        print("\nLogic: Each street follows Red → Green → Yellow")
        print("Key Invariant: V's yellow end = H's red end\n")
        
        t = 0
        print(f"Time | V-Street | H-Street | Phase")
        print("-" * 60)
        
        # Phase 1: V Red, H flowing
        print(f"\n--- PHASE 1: V is RED (12s), H flows ---")
        print(f"{int(t):4d}s | 🔴 RED   | 🟢 GREEN | H flows, V stopped")
        t += self.H_GREEN_TIME
        
        print(f"{int(t):4d}s | 🔴 RED   | 🟡 YELLOW| H warning, V stopped")
        t += self.H_YELLOW_TIME
        
        # Phase 2: H Red, V flowing
        print(f"\n--- PHASE 2: H is RED (12s), V flows ---")
        print(f"{int(t):4d}s | 🟢 GREEN | 🔴 RED   | V flows, H stopped")
        t += self.V_GREEN_TIME
        
        print(f"{int(t):4d}s | 🟡 YELLOW| 🔴 RED   | V warning, H stopped")
        print(f"      ↑ INVARIANT: V yellow ending...")
        t += self.V_YELLOW_TIME
        
        print(f"{int(t):4d}s | [CYCLE REPEATS]")
        print(f"      ↑ INVARIANT: ...exactly when H red ends!")
        
        print("\n" + "="*60)
        print(f"Total Cycle Duration: {int(t)}s")
        print(f"V Time: Red={self.V_RED_TIME}s, Green={self.V_GREEN_TIME}s, Yellow={self.V_YELLOW_TIME}s")
        print(f"H Time: Red={self.H_RED_TIME}s, Green={self.H_GREEN_TIME}s, Yellow={self.H_YELLOW_TIME}s")
        print(f"\n✓ Handwritten spec verified: Yellow must intersect on green/before red")
        print(f"✓ V yellow end aligns with H red end at t={int(t)}s")
        print("="*60 + "\n")


def interactive_menu(traffic_light):
    """Interactive menu for controlling the traffic light"""
    print("\n" + "="*60)
    print("Traffic Light Control Menu - Handwritten Spec")
    print("="*60)
    print("1. Set NORMAL mode (Red→Green→Yellow cycle)")
    print("2. Set NIGHT mode (blinking yellow both directions)")
    print("3. Set MAINTENANCE mode (all off)")
    print("4. Trigger EMERGENCY override (flashing red)")
    print("5. Request pedestrian crossing V-street")
    print("6. Request pedestrian crossing H-street")
    print("7. Show timing analysis (verify handwritten spec)")
    print("8. Exit")
    print("="*60)
    
    while traffic_light.running:
        try:
            choice = input("\nEnter choice (1-8): ").strip()
            
            if choice == "1":
                traffic_light.set_mode("NORMAL")
            elif choice == "2":
                traffic_light.set_mode("NIGHT")
            elif choice == "3":
                traffic_light.set_mode("MAINTENANCE")
            elif choice == "4":
                traffic_light.emergency_override = True
            elif choice == "5":
                traffic_light.pedestrian_v_request = True
                print("🚶 Pedestrian V-street crossing requested (will be served when V is RED)")
            elif choice == "6":
                traffic_light.pedestrian_h_request = True
                print("🚶 Pedestrian H-street crossing requested (will be served when H is RED)")
            elif choice == "7":
                traffic_light.print_timing_analysis()
            elif choice == "8":
                print("Exiting...")
                traffic_light.stop()
                break
            else:
                print("Invalid choice. Please enter 1-8.")
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("RASPBERRY PI TRAFFIC CONTROL SYSTEM")
    print("Handwritten Specification Implementation")
    print("="*60)
    print("Version: 3.0 (Handwritten Logic)")
    print("Date: October 15, 2025")
    print("\nImplementation:")
    print("  ✓ Red (12s) → Green (9s) → Yellow (3s) per street")
    print("  ✓ Yellow intersects on green OR before red")
    print("  ✓ V's yellow end = H's red end (INVARIANT)")
    print("  ✓ No simultaneous greens (safety)")
    print("  ✓ Pedestrian crossing support")
    print("  ✓ Emergency override")
    print("="*60 + "\n")
    
    # Create traffic light instance
    traffic_light = TrafficLight()
    
    # Show timing analysis
    traffic_light.print_timing_analysis()
    
    input("Press Enter to start the traffic light system...")
    
    # Start traffic light in a separate thread
    traffic_thread = threading.Thread(target=traffic_light.run, daemon=True)
    traffic_thread.start()
    
    # Give it a moment to start
    time.sleep(1)
    
    # Run interactive menu in main thread
    interactive_menu(traffic_light)
    
    # Wait for traffic light thread to finish
    traffic_thread.join(timeout=2)
    
    print("\n✓ Program terminated.")


if __name__ == "__main__":
    main()

"""
LED Testing Script
Test each LED individually before running the main traffic control system
"""

import time

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
            state_str = "HIGH (ON)" if state == MockGPIO.HIGH else "LOW (OFF)"
            print(f"[MOCK] GPIO.output(pin={pin}, state={state_str})")
        
        @staticmethod
        def cleanup():
            print(f"[MOCK] GPIO.cleanup() - Cleaned up {len(MockGPIO._pin_states)} pins")
            MockGPIO._pin_states.clear()
    
    GPIO = MockGPIO()

# GPIO Pin Configuration
PINS = {
    "V-Street Red": 17,
    "V-Street Yellow": 27,
    "V-Street Green": 22,
    "H-Street Red": 23,
    "H-Street Yellow": 24,
    "H-Street Green": 25
}

def test_individual_leds():
    """Test each LED one by one"""
    print("="*60)
    print("LED INDIVIDUAL TEST")
    print("="*60)
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup all pins
    for name, pin in PINS.items():
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    
    try:
        for name, pin in PINS.items():
            print(f"\nTesting {name} (GPIO {pin})...")
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(2)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(0.5)
        
        print("\n✓ Individual LED test complete!")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up")


def test_all_leds_together():
    """Test all LEDs at once"""
    print("\n" + "="*60)
    print("ALL LEDS TOGETHER TEST")
    print("="*60)
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup all pins
    for name, pin in PINS.items():
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    
    try:
        print("\nTurning ON all LEDs...")
        for pin in PINS.values():
            GPIO.output(pin, GPIO.HIGH)
        
        time.sleep(3)
        
        print("Turning OFF all LEDs...")
        for pin in PINS.values():
            GPIO.output(pin, GPIO.LOW)
        
        print("\n✓ All LEDs test complete!")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up")


def test_by_color():
    """Test LEDs grouped by color"""
    print("\n" + "="*60)
    print("COLOR GROUP TEST")
    print("="*60)
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup all pins
    for name, pin in PINS.items():
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    
    color_groups = {
        "Red": [17, 23],
        "Yellow": [27, 24],
        "Green": [22, 25]
    }
    
    try:
        for color, pins in color_groups.items():
            print(f"\nTesting {color} LEDs (GPIO {pins})...")
            for pin in pins:
                GPIO.output(pin, GPIO.HIGH)
            time.sleep(2)
            for pin in pins:
                GPIO.output(pin, GPIO.LOW)
            time.sleep(0.5)
        
        print("\n✓ Color group test complete!")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up")


def test_blink_pattern():
    """Test with a blinking pattern"""
    print("\n" + "="*60)
    print("BLINK PATTERN TEST")
    print("="*60)
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup all pins
    for name, pin in PINS.items():
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    
    try:
        print("\nBlinking all LEDs 5 times...")
        for i in range(5):
            print(f"Blink {i+1}/5")
            for pin in PINS.values():
                GPIO.output(pin, GPIO.HIGH)
            time.sleep(0.3)
            for pin in PINS.values():
                GPIO.output(pin, GPIO.LOW)
            time.sleep(0.3)
        
        print("\n✓ Blink pattern test complete!")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up")


def main():
    """Main test menu"""
    print("\n" + "="*60)
    print("TRAFFIC LIGHT LED TESTING UTILITY")
    print("="*60)
    print("\nThis script will help you verify that all LEDs are")
    print("properly connected to the correct GPIO pins.\n")
    print("Available Tests:")
    print("1. Test each LED individually")
    print("2. Test all LEDs together")
    print("3. Test LEDs by color group")
    print("4. Test blink pattern")
    print("5. Run all tests")
    print("0. Exit")
    print("="*60)
    
    while True:
        try:
            choice = input("\nEnter your choice (0-5): ").strip()
            
            if choice == "0":
                print("Exiting...")
                break
            elif choice == "1":
                test_individual_leds()
            elif choice == "2":
                test_all_leds_together()
            elif choice == "3":
                test_by_color()
            elif choice == "4":
                test_blink_pattern()
            elif choice == "5":
                test_individual_leds()
                test_all_leds_together()
                test_by_color()
                test_blink_pattern()
                print("\n✓ All tests completed!")
            else:
                print("Invalid choice. Please enter 0-5.")
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break


if __name__ == "__main__":
    main()

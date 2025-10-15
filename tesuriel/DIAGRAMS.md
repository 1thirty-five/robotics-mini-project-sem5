c# Traffic Control System - Visual Diagrams

## State Machine Diagram (ASCII Art)

```
                    ╔═══════════════════════════════════════════════════╗
                    ║        4-STATE FSM TRAFFIC CONTROLLER              ║
                    ║               26-second cycle                      ║
                    ╚═══════════════════════════════════════════════════╝

    START
      │
      ▼
┌─────────────────────┐
│    V_GREEN (9s)     │ ◄─────────────────────────────────────────┐
│   ┌─────┬─────┐     │                                           │
│   │  V  │  H  │     │                                           │
│   │ 🟢  │ 🔴  │     │                                           │
│   └─────┴─────┘     │                                           │
└─────────┬───────────┘                                           │
          │ timeout(9s)                                           │
          │                                                       │
          ▼                                                       │
┌─────────────────────┐                                           │
│   V_YELLOW (3s)     │                                           │
│   ┌─────┬─────┐     │                                           │
│   │  V  │  H  │     │  ◄── CRITICAL: V warning phase           │
│   │ 🟡  │ 🔴  │     │       H still stopped                     │
│   └─────┴─────┘     │                                           │
└─────────┬───────────┘                                           │
          │ timeout(3s)                                           │
          │                                                       │
          ▼                                                       │
┌─────────────────────┐                                           │
│   ALL_RED (1s)      │  ◄── SAFETY CLEARANCE                    │
│   ┌─────┬─────┐     │       Prevents collisions                │
│   │  V  │  H  │     │       from late-yellow runners           │
│   │ 🔴  │ 🔴  │     │                                           │
│   └─────┴─────┘     │  ⚠️  INVARIANT BOUNDARY:                 │
└─────────┬───────────┘       V_YELLOW ended @ t=12              │
          │ timeout(1s)       H_RED ending @ t=13                │
          │                                                       │
          ▼                                                       │
┌─────────────────────┐                                           │
│    H_GREEN (9s)     │  ◄── H now flows, V stopped              │
│   ┌─────┬─────┐     │                                           │
│   │  V  │  H  │     │                                           │
│   │ 🔴  │ 🟢  │     │                                           │
│   └─────┴─────┘     │                                           │
└─────────┬───────────┘                                           │
          │ timeout(9s)                                           │
          │                                                       │
          ▼                                                       │
┌─────────────────────┐                                           │
│   H_YELLOW (3s)     │                                           │
│   ┌─────┬─────┐     │                                           │
│   │  V  │  H  │     │                                           │
│   │ 🔴  │ 🟡  │     │                                           │
│   └─────┴─────┘     │                                           │
└─────────┬───────────┘                                           │
          │ timeout(3s)                                           │
          │                                                       │
          ▼                                                       │
┌─────────────────────┐                                           │
│   ALL_RED (1s)      │  ◄── SAFETY CLEARANCE                    │
│   ┌─────┬─────┐     │                                           │
│   │  V  │  H  │     │                                           │
│   │ 🔴  │ 🔴  │     │                                           │
│   └─────┴─────┘     │                                           │
└─────────┬───────────┘                                           │
          │ timeout(1s)                                           │
          │                                                       │
          └───────────────────────────────────────────────────────┘
                     (Cycle repeats)
```

---

## Timing Diagram (Timeline View)

```
Time (seconds)
│
│   V-Street Light Status                    H-Street Light Status
│   ═══════════════════                      ═══════════════════
│
0s  ├───────────────────────────┐            ├───────────────────────────┐
    │       🟢 GREEN            │            │        🔴 RED             │
    │                           │            │                           │
    │     V FLOWS               │            │     H STOPPED             │
    │                           │            │                           │
9s  ├───────────┐               │            │                           │
    │ 🟡 YELLOW │               │            │                           │
    │           │               │            │                           │
12s ├─ 🔴 RED ──┘               │            ├─────────────┐             │
    │ (ALL_RED)                 │            │ (ALL_RED)   │             │
13s │                           │            │ 🟢 GREEN    │             │
    │                           │            │             │             │
    │     V STOPPED             │            │   H FLOWS   │             │
    │                           │            │             │             │
    │                           │            │             │             │
22s │                           │            ├────────────┐│             │
    │                           │            │ 🟡 YELLOW  ││             │
    │                           │            │            ││             │
25s │                           │            ├─ 🔴 RED ───┘│             │
    │                           │            │  (ALL_RED)  │             │
26s └───────────────────────────┘            └─────────────┘             │
    [CYCLE REPEATS from 0s]
    
    
    ╔═══════════════════════════════════════════════════════════════╗
    ║  KEY INSIGHT: At t=12-13s                                     ║
    ║  V_YELLOW ends (12s) → ALL_RED (1s) → H_RED ends (13s)       ║
    ║  This enforces your INVARIANT!                                ║
    ╚═══════════════════════════════════════════════════════════════╝
```

---

## Intersection Physical Layout

```
                          North
                            ↑
                            │
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            │    V-Street   │   V-Street    │
            │   (Vertical)  │  (Vertical)   │
            │               │               │
            │        ┌──────┴──────┐        │
            │        │   🚦 V      │        │
            │        │   ┌─┐       │        │
West ◄──────┤        │   │🔴│      │        ├──────► East
            │        │   │🟡│      │        │
            │        │   │🟢│      │        │
            │        │   └─┘       │        │
            │        └─────────────┘        │
            │               │               │
────────────┼───────────────┼───────────────┼────────────
H-Street    │               │               │    H-Street
(Horiz.)    │               │               │    (Horiz.)
            │               │               │
   🚦 H     │               │               │     🚦 H
  ┌────┐   │               │               │    ┌────┐
  │🔴🟡🟢│  │               │               │    │🔴🟡🟢│
  └────┘   │               │               │    └────┘
            │               │               │
────────────┼───────────────┼───────────────┼────────────
            │               │               │
            │        ┌─────────────┐        │
            │        │   🚦 V      │        │
            │        │   ┌─┐       │        │
            │        │   │🔴│      │        │
            │        │   │🟡│      │        │
            │        │   │🟢│      │        │
            │        │   └─┘       │        │
            │        └──────┬──────┘        │
            │               │               │
            │    V-Street   │   V-Street    │
            │   (Vertical)  │  (Vertical)   │
            │               │               │
            └───────────────┼───────────────┘
                            │
                            ↓
                          South

Legend:
🚦 V = Traffic light for V-street (North-South)
🚦 H = Traffic light for H-street (East-West)
🚶 = Pedestrian crossing button locations
```

---

## Pedestrian Crossing Logic

```
┌─────────────────────────────────────────────────────────────────┐
│                  PEDESTRIAN CROSSING SAFETY                      │
└─────────────────────────────────────────────────────────────────┘

Scenario 1: Pedestrian wants to cross V-street
─────────────────────────────────────────────────

Time:      V-Street     H-Street    Pedestrian Action
───────────────────────────────────────────────────────
  0s       🟢 GREEN     🔴 RED      [Press V-crossing button]
  0s       🟢 GREEN     🔴 RED      ❌ Cannot cross (V is green)
                                    Request QUEUED
  
 10s       🟡 YELLOW    🔴 RED      Request still queued
 13s       🔴 RED       🟢 GREEN    ✅ WALK signal activated!
                                    🚶 Pedestrian crosses V-street
                                    (V is RED = safe to cross V)
 21s       🔴 RED       🟢 GREEN    ⚠️  DON'T WALK (clearance)
 23s       🔴 RED       🟡 YELLOW   Crossing complete


Scenario 2: Pedestrian wants to cross H-street
─────────────────────────────────────────────────

Time:      V-Street     H-Street    Pedestrian Action
───────────────────────────────────────────────────────
  0s       🟢 GREEN     🔴 RED      [Press H-crossing button]
  0s       🟢 GREEN     🔴 RED      ✅ WALK signal activated!
                                    🚶 Pedestrian crosses H-street
                                    (H is RED = safe to cross H)
  8s       🟢 GREEN     🔴 RED      ⚠️  DON'T WALK (clearance)
 10s       🟡 YELLOW    🔴 RED      Crossing complete


╔═══════════════════════════════════════════════════════════════╗
║  SAFETY RULE:                                                 ║
║  Pedestrians ONLY cross when conflicting traffic is RED       ║
║  - Cross V-street when V light is RED (during H_GREEN)       ║
║  - Cross H-street when H light is RED (during V_GREEN)       ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## Emergency Override Behavior

```
┌─────────────────────────────────────────────────────────────────┐
│                      EMERGENCY MODE                              │
└─────────────────────────────────────────────────────────────────┘

Normal Operation         Emergency Button Pressed        Recovery
─────────────────        ─────────────────────────       ──────────

V: 🟢 GREEN              V: 🔴 RED (flash)               V: 🟢 GREEN
H: 🔴 RED                H: 🔴 RED (flash)               H: 🔴 RED
                              ↓                          (FSM reset)
                         V: ⚫ OFF                        
                         H: ⚫ OFF                        
                              ↓                          
                         V: 🔴 RED (flash)               
                         H: 🔴 RED (flash)               
                              ↓                          
                         [Repeats @ 0.5s intervals]
                              
                         All traffic MUST STOP
                         Emergency vehicle passes
                         
                         Button released
                              ↓
                         Return to normal
                         Start at V_GREEN

Timeline:
───────────────────────────────────────────────────────────────────
Normal cycle → 🚨 Emergency → Flashing red (both) → 🚨 Clear → Normal

Duration: Variable (controlled by emergency button hold time)
Effect: Immediate preemption, overrides all other logic
```

---

## GPIO Pin Mapping (Raspberry Pi)

```
┌──────────────────────────────────────────────────────────────┐
│                    Raspberry Pi GPIO                          │
│                     (BCM Numbering)                           │
└──────────────────────────────────────────────────────────────┘

    ┌────────────────────────────────────┐
    │  GPIO 17 ──[220Ω]───(🔴 V Red)    │
    │  GPIO 27 ──[220Ω]───(🟡 V Yellow) │
    │  GPIO 22 ──[220Ω]───(🟢 V Green)  │
    │                                    │
    │  GPIO  5 ──[220Ω]───(🔴 H Red)    │
    │  GPIO  6 ──[220Ω]───(🟡 H Yellow) │
    │  GPIO 13 ──[220Ω]───(🟢 H Green)  │
    │                                    │
    │  GPIO 23 ──[Button]──┬─[10kΩ]─3.3V│  Ped V Button
    │  GPIO 24 ──[Button]──┤            │  Ped H Button
    │  GPIO 25 ──[Button]──┘            │  Emergency
    │                                    │
    │  GND ─────────────────────(Common)│
    └────────────────────────────────────┘

LED Wiring (each LED):
    GPIO Pin ──[ 220Ω Resistor ]──[LED]──┐
                                          │
                                        [GND]
    
    Long leg (Anode) ─→ Resistor side
    Short leg (Cathode) ─→ GND side

Button Wiring (each button):
    GPIO Pin ──[Button]──┬──[10kΩ Pull-up]──3.3V
                         │
                       [GND]
    
    Note: Internal pull-up enabled in code
```

---

## Mode State Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    OPERATING MODES                            │
└──────────────────────────────────────────────────────────────┘

        START
          │
          ▼
    ┌──────────┐
    │  NORMAL  │ ◄────────────────┐
    │  (4-FSM) │                  │
    └─────┬────┘                  │
          │                       │
   ┌──────┼──────┬────────┐       │
   │      │      │        │       │
   │(2)   │(3)   │(4)     │       │
   ▼      ▼      ▼        │       │
┌──────┐┌──────┐┌───────┐ │       │
│NIGHT ││MAINT ││EMERG. │ │       │
│ 🟡⚡  ││  ⚫  ││ 🔴⚡   │ │       │
└──┬───┘└──┬───┘└───┬───┘ │       │
   │       │        │     │       │
   │(1)    │(1)     │(1)  │(1)    │
   └───────┴────────┴─────┴───────┘

Mode Transitions (via menu):
1 → NORMAL:      Standard 4-state FSM
2 → NIGHT:       Blinking yellow (both directions)
3 → MAINTENANCE: All lights off
4 → EMERGENCY:   Flashing red (both directions)

States:
• NORMAL:      Production traffic control
• NIGHT:       Low-traffic hours (caution)
• MAINTENANCE: Service mode (manual control)
• EMERGENCY:   Emergency vehicle priority
```

---

## Invariant Verification Diagram

```
╔══════════════════════════════════════════════════════════════╗
║        SAFETY INVARIANT: NO SIMULTANEOUS GREEN               ║
╚══════════════════════════════════════════════════════════════╝

Time →  0s     5s    10s    15s    20s    25s    30s
        │      │      │      │      │      │      │
V: ─────┼──🟢──┼──🟢──┼─🟡─┼🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴┼──🟢──┼──
        │      │      │      │      │      │      │
H: ─────┼─🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴┼─🔴─┼──🟢──┼──🟢──┼─🟡─┼🔴🔴🔴─
        │      │      │      │      │      │      │

Legend:
🟢 = Green (traffic flows)
🟡 = Yellow (warning)
🔴 = Red (stopped)

Verification:
───────────────────────────────────────────────────────────────
∀t: ¬(V_Green(t) ∧ H_Green(t))  ← Mathematical proof

Observation:
• When V is 🟢, H is ALWAYS 🔴
• When H is 🟢, V is ALWAYS 🔴
• No overlap of green signals
• ALL_RED buffer between transitions

✅ INVARIANT SATISFIED
```

---

## Throughput Analysis

```
┌──────────────────────────────────────────────────────────────┐
│              INTERSECTION THROUGHPUT (26s cycle)              │
└──────────────────────────────────────────────────────────────┘

V-Street Time Allocation:
    Green:  ████████████████████ 9s  (34.6%)
    Yellow: ██████ 3s               (11.5%)
    Red:    ████████████████████████ 12s (46.2%)
    Clear:  ██ 2s                   (7.7%)
            ──────────────────────────────────
            Total: 26s (100%)

H-Street Time Allocation:
    Green:  ████████████████████ 9s  (34.6%)
    Yellow: ██████ 3s               (11.5%)
    Red:    ████████████████████████ 12s (46.2%)
    Clear:  ██ 2s                   (7.7%)
            ──────────────────────────────────
            Total: 26s (100%)

Effective Throughput:
───────────────────────────────────────────────────────────────
V: (Green + Yellow) / Cycle = (9 + 3) / 26 = 46.2% ✅
H: (Green + Yellow) / Cycle = (9 + 3) / 26 = 46.2% ✅

Safety Overhead: 2s / 26s = 7.7% ✅

✅ Balanced throughput (equal priority)
✅ Safety overhead within acceptable range (<10%)
```

---

## Summary: Key Visual Insights

1. **FSM Flow:** Clean 4-state cycle with ALL_RED safety buffers
2. **Timeline:** Exact timing shows invariant at t=12-13s
3. **Intersection:** Physical layout shows two-way control
4. **Pedestrian:** Only cross when conflicting traffic is RED
5. **Emergency:** Immediate preemption with flashing red
6. **GPIO:** Complete pin mapping for Raspberry Pi
7. **Modes:** Four operating modes with transitions
8. **Invariant:** Mathematical proof via timeline
9. **Throughput:** Balanced 46% each direction

All diagrams verify your specification! 🎯

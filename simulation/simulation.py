#!/usr/bin/env python3
"""
================================================================
  Solar-Powered Automatic Sanitizer Dispenser — Simulator
  ----------------------------------------------------------------
  Repo   : github.com/YOUR_USERNAME/solar-sanitizer-dispenser
  File   : simulation/simulation.py
  Python : 3.8+  |  No external packages required
================================================================

  Emulates the Arduino firmware state machine on your PC.
  Test timing, battery behaviour, and solar charge/discharge
  without any physical hardware.

  USAGE:
    python simulation.py          # interactive keyboard mode
    python simulation.py --auto   # auto demo (no keyboard)

  CONTROLS (interactive mode):
    ENTER  →  Simulate hand detection
    s      →  Toggle solar panel ON / OFF
    b      →  Print battery status now
    q      →  Quit and show session summary
================================================================
"""

import time
import threading
import argparse
from datetime import datetime

# ── ANSI colour helpers ─────────────────────────────────────
class C:
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    BLUE   = "\033[94m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RESET  = "\033[0m"

def log(tag, msg, color=C.RESET):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"{C.DIM}[{ts}]{C.RESET} {color}{C.BOLD}[{tag:<8}]{C.RESET} {color}{msg}{C.RESET}")

# ── Firmware constants — mirror the .ino ────────────────────
PUMP_ON_S           = 0.8     # seconds pump stays ON
COOLDOWN_S          = 2.0     # seconds cooldown after dispense
BATT_CHECK_S        = 5.0     # seconds between battery prints
VBAT_LOW            = 3.5     # low battery threshold (V)
VBAT_FULL           = 4.2     # fully charged (V)
VBAT_INIT           = 3.90    # starting voltage for simulation

# Battery model — rates in V/second
SOLAR_CHARGE_RATE   = 0.005   # charge rate when solar panel ON
IDLE_DISCHARGE_RATE = 0.0005  # quiescent draw (idle)
PUMP_DISCHARGE_RATE = 0.012   # extra drain during pump ON

# ── State constants ──────────────────────────────────────────
IDLE, PUMPING, COOLDOWN = "IDLE", "PUMPING", "COOLDOWN"

# ════════════════════════════════════════════════════════════
class SanitizerDispenser:
    """Full software emulation of solar_sanitizer.ino"""

    def __init__(self):
        self.state         = IDLE
        self.state_entered = time.time()
        self.vbat          = VBAT_INIT
        self.solar_on      = True
        self.led_green     = False
        self.led_red       = False
        self.dispenses     = 0
        self._lock         = threading.Lock()
        self._running      = False

    # ── Battery simulation ───────────────────────────────────
    def _tick_battery(self, dt: float):
        with self._lock:
            charge = SOLAR_CHARGE_RATE * dt if self.solar_on else 0.0
            if self.state == PUMPING:
                drain = PUMP_DISCHARGE_RATE * dt
            else:
                drain = IDLE_DISCHARGE_RATE * dt
            self.vbat = max(3.0, min(VBAT_FULL, self.vbat + charge - drain))

    # ── LED logic ────────────────────────────────────────────
    def _update_leds(self):
        if self.vbat >= VBAT_LOW:
            self.led_green, self.led_red = True, False
        else:
            self.led_green, self.led_red = False, True

    # ── Public: trigger hand detection ──────────────────────
    def detect_hand(self):
        with self._lock:
            if self.state != IDLE:
                log("IR", "Hand ignored — system busy.", C.DIM)
                return
            self.dispenses    += 1
            self.state         = PUMPING
            self.state_entered = time.time()
        log("IR",   "Hand detected! (sensor LOW)", C.BLUE)
        log("PUMP",  f"ON — dispensing dose #{self.dispenses}  *beep*", C.CYAN)

    # ── Public: toggle solar panel ───────────────────────────
    def toggle_solar(self):
        with self._lock:
            self.solar_on = not self.solar_on
        icon   = "☀️ " if self.solar_on else "🌑"
        status = "connected" if self.solar_on else "disconnected"
        log("SOLAR", f"Panel {icon} {status}", C.YELLOW)

    # ── Public: print battery now ───────────────────────────
    def print_battery(self):
        v   = self.vbat
        pct = max(0, min(100, int(((v - 3.0) / (VBAT_FULL - 3.0)) * 100)))
        bar = ("█" * (pct // 10)).ljust(10, "░")
        sun = "☀️ " if self.solar_on else "  "
        col = C.GREEN if v >= VBAT_LOW else C.RED
        log("BATTERY",
            f"{sun}[{bar}] {pct:3d}%  {v:.2f}V  |  Dispenses: {self.dispenses}",
            col)
        if v < VBAT_LOW:
            log("WARNING", "Low battery — place panel in sunlight!", C.RED)

    # ── Background main loop ─────────────────────────────────
    def _main_loop(self, tick=0.05):
        last_time      = time.time()
        last_batt_log  = time.time()

        while self._running:
            now = time.time()
            dt  = now - last_time
            last_time = now

            self._tick_battery(dt)
            self._update_leds()

            with self._lock:
                # Pump → Cooldown transition
                if self.state == PUMPING:
                    if (now - self.state_entered) >= PUMP_ON_S:
                        self.state         = COOLDOWN
                        self.state_entered = now
                        log("PUMP",     "OFF — dose complete.", C.CYAN)
                        log("COOLDOWN", "2s wait...", C.YELLOW)

                # Cooldown → Idle transition
                elif self.state == COOLDOWN:
                    if (now - self.state_entered) >= COOLDOWN_S:
                        self.state = IDLE
                        log("IDLE", "Ready for next hand.", C.GREEN)

            # Periodic battery log
            if now - last_batt_log >= BATT_CHECK_S:
                last_batt_log = now
                self.print_battery()

            time.sleep(tick)

    def start(self):
        self._running = True
        self._thread  = threading.Thread(target=self._main_loop, daemon=True)
        self._thread.start()
        # Boot sequence
        log("SYSTEM", "=== Solar Sanitizer Dispenser Online ===", C.GREEN)
        log("SYSTEM", "Boot blink x3... LED GREEN + LED RED + BEEP", C.GREEN)
        time.sleep(0.5)
        log("IDLE",   "Waiting for hand detection...", C.GREEN)

    def stop(self):
        self._running = False
        self._thread.join(timeout=2)
        self._print_summary()

    def _print_summary(self):
        print(f"\n{C.BOLD}{'='*48}{C.RESET}")
        print(f"{C.BOLD}  SESSION SUMMARY{C.RESET}")
        print(f"{'='*48}")
        print(f"  Total dispenses  : {self.dispenses}")
        print(f"  Final voltage    : {self.vbat:.2f} V")
        print(f"  Solar panel      : {'ON ☀️' if self.solar_on else 'OFF 🌑'}")
        print(f"  Green LED        : {'ON' if self.led_green else 'OFF'}")
        print(f"  Red LED          : {'ON' if self.led_red else 'OFF'}")
        print(f"{'='*48}\n")


# ════════════════════════════════════════════════════════════
#  INTERACTIVE MODE
# ════════════════════════════════════════════════════════════
def interactive_mode(d: SanitizerDispenser):
    print(f"\n{C.BOLD}CONTROLS:{C.RESET}")
    print("  [ENTER]  →  Simulate hand detection")
    print("  [s]      →  Toggle solar panel on/off")
    print("  [b]      →  Battery status now")
    print("  [q]      →  Quit\n")
    while True:
        try:
            cmd = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        if cmd in ("q", "quit", "exit"):
            break
        elif cmd == "s":
            d.toggle_solar()
        elif cmd == "b":
            d.print_battery()
        else:
            d.detect_hand()


# ════════════════════════════════════════════════════════════
#  AUTO DEMO MODE
# ════════════════════════════════════════════════════════════
def auto_demo(d: SanitizerDispenser):
    log("DEMO", "Running auto-demo scenario (18 seconds)...", C.YELLOW)
    events = [
        (1.5,  "hand"),
        (4.0,  "hand"),
        (6.5,  "solar_off"),
        (8.0,  "hand"),
        (10.0, "solar_on"),
        (12.0, "hand"),
        (14.5, "hand"),
        (16.0, "battery"),
    ]
    start = time.time()
    for delay, event in events:
        time.sleep(max(0, delay - (time.time() - start)))
        if event == "hand":
            d.detect_hand()
        elif event == "solar_off":
            log("DEMO", "Simulating cloud cover...", C.YELLOW)
            d.toggle_solar()
        elif event == "solar_on":
            log("DEMO", "Cloud cleared — sun back!", C.YELLOW)
            d.toggle_solar()
        elif event == "battery":
            d.print_battery()
    time.sleep(2)


# ════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description="Solar Sanitizer Dispenser — Python Simulation"
    )
    parser.add_argument(
        "--auto", action="store_true",
        help="Run automated demo scenario (no keyboard needed)"
    )
    args = parser.parse_args()

    print(f"\n{C.BOLD}{C.GREEN}")
    print("  ☀️  SOLAR-POWERED SANITIZER DISPENSER  ☀️")
    print("  github.com/YOUR_USERNAME/solar-sanitizer-dispenser")
    print(f"{'─'*52}{C.RESET}\n")

    dispenser = SanitizerDispenser()
    dispenser.start()
    time.sleep(0.3)

    try:
        if args.auto:
            auto_demo(dispenser)
        else:
            interactive_mode(dispenser)
    finally:
        dispenser.stop()


if __name__ == "__main__":
    main()

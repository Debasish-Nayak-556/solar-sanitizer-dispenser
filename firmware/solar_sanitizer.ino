/*
 * ============================================================
 *   PROJECT  : Solar-Powered Automatic Sanitizer Dispenser
 *   FILE     : solar_sanitizer.ino
 *   BOARD    : Arduino Uno / Nano
 *   VERSION  : 1.0
 *   AUTHOR   : solar-sanitizer-dispenser
 *   REPO     : github.com/YOUR_USERNAME/solar-sanitizer-dispenser
 * ============================================================
 *
 *  DESCRIPTION:
 *    Touchless sanitizer dispenser powered entirely by a solar
 *    panel + Li-ion battery. An IR sensor detects a hand,
 *    triggers a relay to run the pump for a fixed dose, then
 *    enters a cooldown period before accepting the next hand.
 *    Battery voltage is monitored via a resistor divider and
 *    reported on status LEDs + Serial console.
 *
 *  PIN MAPPING:
 *  ┌──────────────────────────────────────────────────────┐
 *  │ Arduino Pin │ Connected To          │ Direction      │
 *  ├─────────────┼───────────────────────┼────────────────┤
 *  │ D2          │ IR Sensor OUT         │ INPUT          │
 *  │ D3          │ Relay IN              │ OUTPUT         │
 *  │ D4          │ Green LED (solar OK)  │ OUTPUT         │
 *  │ D5          │ Red LED (low battery) │ OUTPUT         │
 *  │ D6          │ Buzzer                │ OUTPUT         │
 *  │ A0          │ Voltage divider node  │ ANALOG INPUT   │
 *  └─────────────┴───────────────────────┴────────────────┘
 *
 *  POWER PATH:
 *    Solar Panel (6V/3W)
 *      → TP4056 Charger Module
 *        → 18650 Li-ion Battery (3.7V 3000mAh)
 *          → MT3608 Boost Converter (5V output)
 *            → Arduino + Relay + Pump
 *
 *  VOLTAGE DIVIDER (battery monitor on A0):
 *    BAT+ ─── R1(10kΩ) ─── A0 ─── R2(4.7kΩ) ─── GND
 *    V_bat = analogRead(A0) * (5.0/1023.0) * ((R1+R2)/R2)
 *
 *  WIRING NOTES:
 *    IR sensor : VCC→5V, GND→GND, OUT→D2 (active LOW output)
 *    Relay     : VCC→5V, GND→GND, IN→D3
 *                COM→battery+, NO→pump+, pump– →GND
 *    LEDs      : 330Ω series resistor on each anode
 *    Buzzer    : positive→D6, negative→GND
 * ============================================================
 */

// ── Pin Definitions ─────────────────────────────────────────
#define PIN_IR_SENSOR    2    // IR sensor output  (active LOW)
#define PIN_RELAY        3    // Relay coil drive  (HIGH = pump ON)
#define PIN_LED_GREEN    4    // Green LED         (solar / battery OK)
#define PIN_LED_RED      5    // Red LED           (low battery warning)
#define PIN_BUZZER       6    // Piezo buzzer
#define PIN_VBAT         A0   // Battery voltage via resistor divider

// ── Timing Constants ────────────────────────────────────────
const unsigned long PUMP_ON_MS          = 800;   // pump ON duration per dose (ms)
const unsigned long COOLDOWN_MS         = 2000;  // wait before next dispense (ms)
const unsigned long BATT_CHECK_INTERVAL = 5000;  // battery check interval (ms)

// ── Battery / Resistor Constants ────────────────────────────
const float R1_KOHM  = 10.0;  // voltage divider top resistor (kΩ)
const float R2_KOHM  =  4.7;  // voltage divider bottom resistor (kΩ)
const float VREF     =  5.0;  // Arduino ADC reference voltage
const float VBAT_LOW =  3.5;  // warn threshold (V)
const float VBAT_FULL = 4.2;  // fully charged voltage (V)

// ── State Machine ───────────────────────────────────────────
enum State { IDLE, PUMPING, COOLDOWN };
State currentState = IDLE;

unsigned long stateEnteredAt = 0;
unsigned long lastBattCheck  = 0;
unsigned int  totalDispenses = 0;

// ════════════════════════════════════════════════════════════
void setup() {
  Serial.begin(9600);

  pinMode(PIN_IR_SENSOR, INPUT);
  pinMode(PIN_RELAY,     OUTPUT);
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_RED,   OUTPUT);
  pinMode(PIN_BUZZER,    OUTPUT);

  // Safe startup state
  digitalWrite(PIN_RELAY,     LOW);
  digitalWrite(PIN_LED_GREEN, LOW);
  digitalWrite(PIN_LED_RED,   LOW);

  bootSequence();

  Serial.println(F("================================================"));
  Serial.println(F("  ☀️  Solar Sanitizer Dispenser  |  v1.0 Ready"));
  Serial.println(F("  github.com/YOUR_USERNAME/solar-sanitizer-dispenser"));
  Serial.println(F("================================================"));
  Serial.println(F("  [IDLE] Waiting for hand detection..."));
}

// ════════════════════════════════════════════════════════════
void loop() {
  unsigned long now = millis();

  // ── 1. Non-blocking state transitions ─────────────────
  switch (currentState) {

    case PUMPING:
      if (now - stateEnteredAt >= PUMP_ON_MS) {
        stopPump();
        enterCooldown(now);
      }
      break;

    case COOLDOWN:
      if (now - stateEnteredAt >= COOLDOWN_MS) {
        enterIdle();
      }
      break;

    case IDLE:
      // sensor check handled below
      break;
  }

  // ── 2. IR hand detection (only when IDLE) ─────────────
  if (currentState == IDLE) {
    if (digitalRead(PIN_IR_SENSOR) == LOW) {   // active LOW
      startPump(now);
    }
  }

  // ── 3. Periodic battery voltage check ─────────────────
  if (now - lastBattCheck >= BATT_CHECK_INTERVAL) {
    lastBattCheck = now;
    float vbat = readBatteryVoltage();
    updateBatteryLEDs(vbat);
    printBatteryStatus(vbat);
  }
}

// ════════════════════════════════════════════════════════════
//  STATE HELPERS
// ════════════════════════════════════════════════════════════

void startPump(unsigned long now) {
  totalDispenses++;
  digitalWrite(PIN_RELAY, HIGH);
  currentState   = PUMPING;
  stateEnteredAt = now;
  shortBeep();
  Serial.print(F("[PUMP ON ] Dispensing dose #"));
  Serial.println(totalDispenses);
}

void stopPump() {
  digitalWrite(PIN_RELAY, LOW);
  Serial.println(F("[PUMP OFF] Dose complete."));
}

void enterCooldown(unsigned long now) {
  currentState   = COOLDOWN;
  stateEnteredAt = now;
  Serial.println(F("[COOLDOWN] 2s wait..."));
}

void enterIdle() {
  currentState = IDLE;
  Serial.println(F("[IDLE    ] Ready for next hand."));
}

// ════════════════════════════════════════════════════════════
//  BATTERY MONITORING
// ════════════════════════════════════════════════════════════

float readBatteryVoltage() {
  int   raw  = analogRead(PIN_VBAT);
  float vadc = raw * (VREF / 1023.0);
  return vadc * ((R1_KOHM + R2_KOHM) / R2_KOHM);
}

void updateBatteryLEDs(float vbat) {
  if (vbat >= VBAT_LOW) {
    digitalWrite(PIN_LED_GREEN, HIGH);
    digitalWrite(PIN_LED_RED,   LOW);
  } else {
    digitalWrite(PIN_LED_GREEN, LOW);
    digitalWrite(PIN_LED_RED,   HIGH);
    longBeep();
  }
}

void printBatteryStatus(float vbat) {
  int pct = constrain(
    (int)(((vbat - 3.0f) / (VBAT_FULL - 3.0f)) * 100.0f), 0, 100);
  Serial.print(F("[BATTERY ] "));
  Serial.print(vbat, 2);
  Serial.print(F("V | "));
  Serial.print(pct);
  Serial.print(F("% | Dispenses today: "));
  Serial.println(totalDispenses);
  if (vbat < VBAT_LOW)
    Serial.println(F("[WARNING ] Low battery — place panel in sunlight!"));
}

// ════════════════════════════════════════════════════════════
//  BUZZER
// ════════════════════════════════════════════════════════════

void shortBeep() {
  digitalWrite(PIN_BUZZER, HIGH);
  delay(80);
  digitalWrite(PIN_BUZZER, LOW);
}

void longBeep() {
  digitalWrite(PIN_BUZZER, HIGH);
  delay(350);
  digitalWrite(PIN_BUZZER, LOW);
}

// ════════════════════════════════════════════════════════════
//  BOOT SEQUENCE  (3x blink on power-on)
// ════════════════════════════════════════════════════════════

void bootSequence() {
  for (int i = 0; i < 3; i++) {
    digitalWrite(PIN_LED_GREEN, HIGH);
    digitalWrite(PIN_LED_RED,   HIGH);
    shortBeep();
    delay(150);
    digitalWrite(PIN_LED_GREEN, LOW);
    digitalWrite(PIN_LED_RED,   LOW);
    delay(150);
  }
}

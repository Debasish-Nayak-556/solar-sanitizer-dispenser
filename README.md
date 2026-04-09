# ☀️ Solar-Powered Automatic Sanitizer Dispenser

![Arduino](https://img.shields.io/badge/Arduino-Nano-00979D?style=flat&logo=arduino&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Platform](https://img.shields.io/badge/Platform-Arduino%20Nano-blue?style=flat)
![Power](https://img.shields.io/badge/Power-Solar%20%2B%20Battery-orange?style=flat)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat)

> **Touchless · Solar-Powered · Zero Electricity Cost · Rural-Ready**

A fully automatic hand sanitizer dispenser that runs 100% on solar energy.
No electricity bill. No touching the device. No internet required.
Built with an Arduino Nano, IR proximity sensor, and a mini pump — perfect for schools, hospitals, public washrooms, and rural areas.

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ System Architecture](#-system-architecture)
- [🔩 Hardware Components](#-hardware-components)
- [⚡ Circuit & Wiring](#-circuit--wiring)
- [🛠️ Hardware Assembly](#-hardware-assembly)
- [💻 Software — Firmware](#-software--firmware)
- [🐍 Software — Python Simulation](#-software--python-simulation)
- [📁 Repository Structure](#-repository-structure)
- [⚡ Power Budget](#-power-budget)
- [🧾 Bill of Materials](#-bill-of-materials)
- [🧪 Testing & Calibration](#-testing--calibration)
- [🔧 Troubleshooting](#-troubleshooting)
- [🚀 Future Enhancements](#-future-enhancements)
- [🌍 Social Impact](#-social-impact)
- [📄 License](#-license)

---

## ✨ Features

| Feature | Detail |
|---|---|
| ☀️ Solar Powered | 6V 3W panel + TP4056 Li-ion charger module |
| 🔋 Battery Backup | 18650 3000mAh — runs 60+ hours without sunlight |
| ✋ Touchless IR | Detects hand within 5–10 cm, dispenses in under 1 second |
| 💧 Precise Dosing | 800 ms pump pulse ≈ 1 mL per dispense |
| 🟢 Solar Status LED | Green LED confirms charging and battery OK |
| 🔴 Low Battery LED | Red LED + long beep warns when battery drops below 3.5V |
| 🔔 Beep Feedback | Piezo buzzer confirms each successful dispense |
| 🌾 Rural-Ready | No Wi-Fi, no internet, no grid power required |
| 🐍 Python Simulator | Test all logic on PC before building hardware |

---

## 🏗️ System Architecture

```
☀️ Solar Panel (6V/3W)
        │
        ▼
┌───────────────┐
│  TP4056       │  Safely charges the Li-ion battery
│  Charger      │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  18650        │  3.7V / 3000mAh energy storage
│  Battery      │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  MT3608       │  Boosts 3.7V → stable 5V
│  Boost Conv.  │
└───────┬───────┘
        │ 5V regulated
        ├──────────────────────┬──────────────────────┐
        ▼                      ▼                      ▼
┌──────────────┐      ┌──────────────┐       ┌──────────────┐
│  Arduino     │◄─────│  IR Sensor   │       │  Relay +     │
│  Nano        │─────►│  FC-51       │       │  Pump Motor  │
│              │      └──────────────┘       └──────────────┘
│  D2 ◄── IR   │
│  D3 ──► Relay│──────────────────────────────────────────►
│  D4 ──► 🟢  │  Green LED
│  D5 ──► 🔴  │  Red LED
│  D6 ──► 🔔  │  Buzzer
│  A0 ◄── BAT  │◄── Voltage divider (10kΩ + 4.7kΩ)
└──────────────┘
```

**State machine flow:**
```
[IDLE] ──(hand detected)──► [PUMPING 800ms] ──(done)──► [COOLDOWN 2s] ──► [IDLE]
```

---

## 🔩 Hardware Components

### ⚡ Power Subsystem

| Component | Specification | Role |
|---|---|---|
| Solar Panel | 6V, 3W polycrystalline | Primary renewable power source |
| 18650 Li-ion Battery | 3.7V, 3000mAh (protected) | Energy storage for day + night |
| TP4056 Module | With overcharge/discharge protection | Safely charges battery from solar |
| MT3608 Boost Converter | 2–24V input → 5V, 2A output | Steps battery voltage up to 5V |

### 🧠 Control & Sensing

| Component | Specification | Role |
|---|---|---|
| Arduino Nano | ATmega328P, 5V, 16MHz | Main microcontroller / brain |
| IR Proximity Sensor | FC-51 or TCRT5000 module | Detects hand within 5–10 cm |
| 5V Relay Module | Opto-isolated, 1-channel | Switches pump power safely |
| Mini DC Pump | 3–5V submersible | Draws and ejects sanitizer liquid |

### 💡 Feedback & Monitoring

| Component | Specification | Role |
|---|---|---|
| Green LED | 5mm, 2V, 20mA | Battery OK / solar charging indicator |
| Red LED | 5mm, 2V, 20mA | Low battery warning |
| Piezo Buzzer | Active, 5V | Audible confirmation per dispense |
| Resistor R1 | 10 kΩ, 1/4W | Voltage divider upper arm |
| Resistor R2 | 4.7 kΩ, 1/4W | Voltage divider lower arm |
| Resistor (×2) | 330 Ω, 1/4W | LED current limiters |
| Silicone Tube | 6mm ID, food-grade, 30cm | Sanitizer flow path |

---

## ⚡ Circuit & Wiring

### Arduino Nano Pin Map

| Pin | Direction | Connected To | Notes |
|---|---|---|---|
| `D2` | INPUT | IR Sensor OUT | Active LOW — LOW = hand detected |
| `D3` | OUTPUT | Relay IN | HIGH = pump ON |
| `D4` | OUTPUT | Green LED (+ 330Ω) | Solar / battery OK |
| `D5` | OUTPUT | Red LED (+ 330Ω) | Low battery warning |
| `D6` | OUTPUT | Piezo Buzzer + | HIGH = beep |
| `A0` | ANALOG IN | Voltage divider node | Battery monitor |
| `5V` | POWER | Sensor VCC, Relay VCC | From MT3608 output |
| `GND` | GROUND | All component GNDs | Common reference |

### Voltage Divider Formula

```
Battery+ ─── R1 (10kΩ) ─── A0 ─── R2 (4.7kΩ) ─── GND

V_battery = analogRead(A0) × (5.0 / 1023) × ((10 + 4.7) / 4.7)
          = analogRead(A0) × 0.01532
```

> 📁 See `schematics/circuit_connections.txt` for full wiring details.
> Add your Fritzing `.fzz` or image to the `schematics/` folder.

---

## 🛠️ Hardware Assembly

| Step | What to do |
|---|---|
| **Step 1** ☀️ | Connect solar panel → TP4056 IN+/IN–. Connect 18650 battery → TP4056 BAT+/BAT–. Wire TP4056 OUT → MT3608 IN. Adjust MT3608 trim pot until output is exactly **5.00V** (use multimeter). |
| **Step 2** 🔌 | Solder R1 (10kΩ) between battery+ and a junction node. Solder R2 (4.7kΩ) from junction to GND. Wire junction node → Arduino A0. |
| **Step 3** 👁️ | Connect IR sensor: VCC→5V, GND→GND, OUT→D2. Adjust onboard potentiometer until sensor triggers at **5–8 cm**. |
| **Step 4** 💧 | Connect relay: VCC→5V, GND→GND, IN→D3. Wire relay COM→battery+, NO→pump+, pump–→GND. Route silicone tube: bottle → pump → nozzle. |
| **Step 5** 💡 | Wire Green LED with 330Ω from D4 to GND. Wire Red LED with 330Ω from D5 to GND. Connect buzzer + → D6, buzzer – → GND. |
| **Step 6** 📦 | Mount all components in enclosure. Fix solar panel on top or outside. Seal the box (weatherproof if outdoors). |

---

## 💻 Software — Firmware

### File: `firmware/solar_sanitizer.ino`

Upload to Arduino Nano using **Arduino IDE 2.x**:
1. Open Arduino IDE → File → Open → select `firmware/solar_sanitizer.ino`
2. Board: **Arduino Nano** | Processor: **ATmega328P (Old Bootloader)**
3. Select correct COM port
4. Click **Upload** ⬆️
5. Open Serial Monitor at **9600 baud** to see live logs

### Serial Monitor Output

```
================================================
  ☀️  Solar Sanitizer Dispenser  |  v1.0 Ready
================================================
  [IDLE    ] Waiting for hand detection...
  [PUMP ON ] Dispensing dose #1
  [PUMP OFF] Dose complete.
  [COOLDOWN] 2s wait...
  [IDLE    ] Ready for next hand.
  [BATTERY ] 3.87V | 81% | Dispenses today: 1
```

### Tunable Constants

| Constant | Default | What it controls |
|---|---|---|
| `PUMP_ON_MS` | `800` ms | Dose size — increase for more sanitizer per press |
| `COOLDOWN_MS` | `2000` ms | Gap between dispenses — prevents accidental double press |
| `VBAT_LOW` | `3.5` V | Threshold for red LED warning |
| `BATT_CHECK_INTERVAL` | `5000` ms | How often ADC reads battery voltage |

---

## 🐍 Software — Python Simulation

### File: `simulation/simulation.py`

Test the complete firmware logic on your PC — no hardware needed.

**Requirements:** Python 3.8+ — no external packages required

```bash
# Interactive mode (keyboard controlled)
cd simulation
python simulation.py

# Controls:
#   ENTER  →  Simulate hand detection
#   s      →  Toggle solar panel on/off
#   b      →  Print battery status now
#   q      →  Quit and show session summary

# Auto demo mode (great for presentations)
python simulation.py --auto
```

### Sample Output

```
☀️  SOLAR-POWERED SANITIZER DISPENSER  ☀️

[12:03:01.042] [SYSTEM  ] === Solar Sanitizer Dispenser Online ===
[12:03:01.544] [IR      ] Hand detected! (sensor LOW)
[12:03:01.545] [PUMP    ] ON — dispensing dose #1  *beep*
[12:03:02.348] [PUMP    ] OFF — dose complete.
[12:03:02.349] [COOLDOWN] 2s wait...
[12:03:04.350] [IDLE    ] Ready for next hand.
[12:03:06.042] [BATTERY ] ☀️  [████████░░]  81%  3.97V  |  Dispenses: 1
```

---

## 📁 Repository Structure

```
solar-sanitizer-dispenser/
│
├── 📄 README.md                        ← You are here
├── 📄 LICENSE                          ← MIT License
│
├── 📂 firmware/                        ← Arduino code (upload to hardware)
│   └── ⚙️  solar_sanitizer.ino
│
├── 📂 simulation/                      ← Python desktop emulator
│   └── 🐍 simulation.py
│
├── 📂 docs/                            ← Project documentation
│   ├── 📘 Solar_Sanitizer_Report.docx  ← Full project report
│   └── 📋 bill_of_materials.csv        ← Components & prices
│
└── 📂 schematics/                      ← Circuit diagrams & wiring
    └── 🔌 circuit_connections.txt      ← Wiring reference guide
```

---

## ⚡ Power Budget

| State | Current Draw | Duration |
|---|---|---|
| Arduino Nano (idle) | ~15 mA | Continuous |
| IR Sensor module | ~20 mA | Continuous |
| Relay coil (when on) | ~70 mA | 0.8s per dispense |
| Pump motor | ~150 mA | 0.8s per dispense |
| LED (1 active) | ~10 mA | Continuous |
| **Total quiescent** | **~45 mA** | |

**Battery life without solar (3000 mAh):**
```
3000 mAh ÷ 45 mA ≈ 66 hours (without any dispensing)
With 100 dispenses/day ≈ 60+ hours  ✅
```

**Solar recharge (6V 3W panel, 5 sun-hours/day):**
```
Panel current = 3W ÷ 6V = 500 mA
Daily charge  = 500 mA × 5 hrs = 2500 mAh
Daily use     = 45 mA × 24 hrs = 1080 mAh
Surplus/day   = +1420 mAh  ✅ Runs indefinitely in good sunlight
```

---

## 🧾 Bill of Materials

| Component | Spec | Qty | Cost (INR) |
|---|---|---|---|
| Solar Panel | 6V, 3W | 1 | ₹150–200 |
| 18650 Battery | 3.7V, 3000mAh | 1 | ₹120–180 |
| TP4056 Charger | With protection | 1 | ₹20–35 |
| MT3608 Boost | → 5V, 2A | 1 | ₹30–50 |
| Arduino Nano | ATmega328P | 1 | ₹180–250 |
| IR Sensor | FC-51 module | 1 | ₹30–50 |
| Mini DC Pump | 3–5V submersible | 1 | ₹80–120 |
| Relay Module | 5V, 1-channel | 1 | ₹40–60 |
| Resistors + LEDs | 10k, 4.7k, 330Ω, LEDs | 1 set | ₹10 |
| Piezo Buzzer | Active 5V | 1 | ₹10–15 |
| Silicone Tube | 6mm ID, 30cm | 1 | ₹20–30 |
| Sanitizer Bottle | 250–500 mL | 1 | ₹30–50 |
| Wires + PCB | Hookup set | 1 | ₹60–110 |
| Enclosure | Plastic/wood box | 1 | ₹50–150 |
| **TOTAL** | | | **₹850–₹1,300** |

> 📋 Full BOM with supplier links: `docs/bill_of_materials.csv`

---

## 🧪 Testing & Calibration

**Test 1 — IR sensor range**
Open Serial Monitor (9600 baud). Wave hand at different distances. Adjust the blue potentiometer on the sensor module until it triggers reliably at **5–8 cm** and not beyond **12 cm**.

**Test 2 — Pump dose size**
Change `PUMP_ON_MS` in firmware. Upload and dispense into a measuring syringe. Target: **0.8–1.5 mL per press**. 800ms ≈ 1mL with a standard 3V pump.

**Test 3 — Voltage divider accuracy**
Measure battery with a multimeter. Compare to `[BATTERY]` output in Serial Monitor. Acceptable error: ±0.1V.

**Test 4 — Full solar cycle**
Place panel in direct sunlight for 2 hours. Verify voltage increases in Serial Monitor. Cover panel — verify red LED lights when voltage drops below 3.5V.

---

## 🔧 Troubleshooting

| Problem | Likely Cause | Fix |
|---|---|---|
| Pump doesn't activate | Relay not switching | Check D3 → Relay IN wire; listen for relay click |
| Continuous dispensing | IR too sensitive | Turn IR potentiometer clockwise to reduce range |
| No dispense on hand | IR range too small | Turn IR potentiometer counter-clockwise |
| Battery not charging | Panel not connected properly | Check panel polarity; ensure ≥ 4.5V in sunlight |
| Red LED always on | Battery deeply discharged | Leave in direct sunlight for 4–6 hours |
| Arduino resets randomly | Unstable 5V supply | Add 100µF capacitor across 5V and GND on MT3608 out |
| Wrong battery reading | Wrong resistor values | Verify R1=10kΩ, R2=4.7kΩ with multimeter |

---

## 🚀 Future Enhancements

- [ ] 📱 **IoT Dashboard** — ESP8266 reports dispense count + battery to web dashboard via Wi-Fi
- [ ] 📲 **SMS Refill Alerts** — SIM800L GSM module sends SMS when sanitizer is low
- [ ] 📏 **Level Sensor** — HC-SR04 ultrasonic measures remaining sanitizer volume
- [ ] 🖥️ **OLED Display** — 0.96" I2C OLED shows battery %, dispense count, solar status
- [ ] 🌧️ **Weatherproof Enclosure** — IP65-rated box for outdoor / monsoon deployment
- [ ] 🔢 **Flow Meter** — Measures exact mL dispensed per activation for audit logging
- [ ] 🔋 **Larger Battery Bank** — 3× 18650 parallel for 3–4 day backup without sun

---

## 🌍 Social Impact

This project directly supports:
- 🎯 **UN SDG Goal 6** — Clean Water & Sanitation
- 🎯 **UN SDG Goal 7** — Affordable & Clean Energy

By making touchless hand hygiene accessible in electricity-deprived rural areas at under ₹1,300 — a fraction of the cost of commercial alternatives.

---

## 📄 License

This project is open-source under the **MIT License**.
Free to use, modify, and distribute for educational and humanitarian purposes.

See [`LICENSE`](LICENSE) for full terms.

---

*Built with ☀️ and 💧 | Designed for rural India and beyond*

**⭐ If this project helped you, please star the repository!**

## PA.I.D.K3a: Calculating: Time, climb and descent rates, course, distance, heading, true airspeed, and groundspeed


### 1. The Oral Standard (The Direct Answer)
Calculating these navigational elements requires applying the wind triangle to convert a map's True Course into a flyable Compass Heading, and utilizing the aircraft's performance charts to determine accurate speeds and climb/descent rates. A pilot measures True Course and distance, applies forecast winds aloft to find the Wind Correction Angle (WCA) and Groundspeed (GS), applies magnetic variation to find Magnetic Heading (MH), and uses the aircraft compass deviation card to find the final Compass Heading (CH).

### 2. The Expert Deep Dive (The "Textbook")
**Regulatory Basis:** 14 CFR 91.103 mandates familiarity with all available information, which implicitly requires accurate mathematical preflight planning to ensure the flight can be completed safely within the aircraft's operational limitations.1

**The "Why":** The physics of air navigation dictate that an aircraft moves within a fluid, moving mass (the air). True Airspeed (TAS) is the speed of the aircraft moving through that airmass, while Groundspeed (GS) is the speed of the aircraft shadow moving over the earth.6 To calculate accurate headings, the sequence is rigid: True Course (TC) ± Wind Correction Angle (WCA) = True Heading (TH).24 From there, TH ± Variation (VAR) = Magnetic Heading (MH), and MH ± Deviation (DEV) = Compass Heading (CH).6 Climb and descent rates must be meticulously calculated using POH charts to determine the exact geographic location of the Top of Climb (TOC) and Top of Descent (TOD), ensuring the aircraft clears en route obstacles and arrives at pattern altitude safely without shock-cooling the engine during a rapid dive.25

| Calculation | Formula / Method | Purpose |
| :--- | :--- | :--- |
| True Heading (TH) | TC ± Wind Correction Angle (WCA) | Compensates for the physical drift caused by winds aloft. |
| Magnetic Heading (MH) | TH ± Magnetic Variation (East is least, West is best) | Aligns the course with the Earth's magnetic poles instead of True North. |
| Compass Heading (CH) | MH ± Compass Deviation | Corrects for electromagnetic interference from the aircraft's own avionics. |
| Time En Route (ETE) | Distance / Groundspeed | Determines exact fuel burn and waypoint arrival times. |

**Scenario Application:** A pilot measures a 90 NM leg with a True Course of 090°. The calculated TAS is 110 knots. Winds aloft are forecast from 045° at 20 knots. Using a mechanical E6B or an electronic flight computer, the pilot calculates a WCA of -7° (left) and a GS of 95 knots. The True Heading is 083°. Local variation is 10° West, making the Magnetic Heading 093°.6 Time en route is Distance divided by Groundspeed: 90 NM / 95 knots = 0.94 hours (which converts to roughly 56 minutes).27

### 3. Common Errors & Gotchas
* **East/West Variation Errors:** Forgetting the fundamental rule "East is least, West is best." Pilots frequently subtract West variation instead of adding it when moving from True to Magnetic calculations.24
* **Confusing TAS with IAS in cruise calculations:** Calculating cross-country travel times using Indicated Airspeed (IAS) instead of True Airspeed (TAS), resulting in massive ETA errors, especially at higher cruising altitudes where TAS is significantly faster than what the airspeed indicator shows.24

### 4. Bridge Keys (Metadata)
* **Regs:** 14 CFR 91.103
* **Docs:** FAA-H-8083-25 (PHAK Ch 16)
* **Keywords:** True Course, Magnetic Heading, Wind Correction Angle, Groundspeed, Top of Descent, Wind Triangle
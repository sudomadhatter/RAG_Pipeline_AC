## PA.I.G.K1g: Avionics

### 1. The Oral Standard (The Direct Answer)
Modern avionics systems replace mechanical gyroscopes and pneumatic instruments with highly integrated glass cockpits, utilizing Primary Flight Displays (PFD) and Multi-Function Displays (MFD). These digital screens are driven by precise solid-state computers: the Air Data Computer (ADC) for airspeed and altitude, and the Attitude and Heading Reference System (AHRS) for pitch, roll, and yaw data.

### 2. The Expert Deep Dive (The "Textbook")

**Regulatory Basis:** 14 CFR 91.205 outlines the mandatory flight instruments for VFR and IFR flight. In technically advanced aircraft (TAA), these regulatory requirements are satisfied through digital replication governed by the system redundancy rules of 14 CFR 23.2500.

**The "Why":** The ADC renders traditional pitot-static instruments obsolete. It connects to the pitot tube and static port and utilizes microscopic, highly sensitive electronic pressure transducers to measure dynamic and ambient air pressure. The computer calculates true airspeed, vertical speed, and altitude in real-time, displaying them as digital tapes. The AHRS eliminates heavy, unreliable vacuum pumps. It relies on Micro Electro-Mechanical Systems (MEMS), which include vibrating microscopic rate sensors, solid-state accelerometers, and a remote flux-valve magnetometer mounted in the wing. Because there are no spinning mechanical masses, the AHRS is entirely immune to gyroscopic precession and tumbling errors. The PFD receives data streams from both the ADC and AHRS to synthesize a unified artificial horizon and flight data picture.

**Scenario Application:** While flying in hard Instrument Meteorological Conditions (IMC), the primary PFD screen suddenly goes completely black due to a backlight inverter failure. Because the ADC and AHRS computers are physically separate units installed deep within the fuselage, they are likely still functioning perfectly. The pilot immediately presses the reversionary mode button on the audio panel. The system reroutes the vital ADC and AHRS data streams to the co-pilot's Multi-Function Display (MFD), seamlessly restoring the artificial horizon, airspeed, and altitude tapes, allowing the pilot to safely execute the instrument approach without relying on the tiny standby analog gauges.

### 3. Common Errors & Gotchas
* **Screen Failure vs. System Failure:** Treating a blank screen as a total system loss. A screen failure is a display issue; an ADC or AHRS failure is a sensor issue. If the AHRS fails, a large red "X" will appear over the attitude indicator, but the airspeed and altitude tapes (driven by the independent ADC) will remain perfectly functional.
* **Impatient Taxiing:** Moving the aircraft before the AHRS has completely aligned on the ramp. The solid-state accelerometers require a stationary period to establish a baseline gravity vector. Moving the aircraft during initialization corrupts the algorithm, inducing subtle attitude errors that manifest during flight.

### 4. Bridge Keys (Metadata)
* **Regs:** 14 CFR 91.205, 14 CFR 23.2500
* **Docs:** FAA-H-8083-25C Chapter 8
* **Keywords:** AHRS, ADC, MEMS, Magnetometer, Reversionary Mode, Transducer, Technically Advanced Aircraft
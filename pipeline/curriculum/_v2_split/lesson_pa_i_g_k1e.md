## PA.I.G.K1e: Fuel, oil, and hydraulic

### 1. The Oral Standard (The Direct Answer)
The fuel system safely stores and delivers proper aviation fuel to the powerplant via gravity feed or mechanical pumps. The oil system circulates lubricant to prevent friction, cool internal components, clean away debris, and seal the cylinders. The hydraulic system uses pressurized fluid to transmit mechanical force, commonly actuating the aircraft's disc brakes and retractable landing gear.

### 2. The Expert Deep Dive (The "Textbook")

**Regulatory Basis:** Aircraft certification rules mandate that gravity-fed fuel systems must be designed to provide a continuous flow rate of 150% of the engine's maximum takeoff fuel consumption, whereas pump-fed systems must provide 125% flow capability.

**The "Why":** High-wing aircraft primarily utilize gravity-feed systems, relying on hydrostatic head pressure to constantly force fuel down into the carburetor float chamber. Low-wing aircraft cannot rely on gravity to overcome the vertical distance to the engine; they require an engine-driven mechanical fuel pump, backed up by an electric auxiliary boost pump for redundancy during critical phases of flight (takeoff and landing). Oil is critical for the survivability of the reciprocating engine. Beyond reducing friction, oil absorbs massive amounts of thermal energy from the cylinder heads and carries it to the oil cooler radiator. Hydraulic systems rely entirely on Pascal's Law. Because hydraulic fluid is virtually incompressible, pressure applied to a confined fluid (by pressing the brake pedals) is transmitted equally and undiminished in all directions ($P=F/A$). A small force applied over a small master cylinder creates an immense clamping force on the large brake caliper pistons.

| System Type | Core Physical Principle | Primary Vulnerability |
| :--- | :--- | :--- |
| **Gravity-Feed Fuel** | Hydrostatic Head Pressure | Fuel starvation in sustained negative-G maneuvers or uncoordinated flight. |
| **Pump-Feed Fuel** | Mechanical/Electrical Suction | Mechanical shearing of the engine-driven pump drive shaft. |
| **Wet-Sump Oil** | Viscous fluid dynamics and heat transfer | Rapid total loss of oil if the oil cooler line ruptures, leading to engine seizure. |
| **Hydraulic Brakes** | Pascal's Law ($P=F/A$) | Fluid leaks leading to the introduction of compressible air bubbles, causing "spongy" or completely failed brakes. |

**Scenario Application:** An aircraft is parked outside overnight with half-empty fuel tanks. As the ambient temperature drops below the dewpoint, the atmosphere inside the fuel tanks reaches saturation, causing water vapor to condense on the aluminum tank walls and drip into the fuel. Because water is heavier than 100LL aviation fuel, it sinks to the lowest points in the system (the sumps). During the preflight inspection, the pilot drains the sumps and visually identifies the water bubbles at the bottom of the tester cup, ensuring the engine will not ingest water and suffer combustion failure on the takeoff roll.

### 3. Common Errors & Gotchas
* **Fuel Grade Cross-Contamination:** Misidentifying fuel colors. 100LL is dyed blue. Jet-A is straw-colored (clear). Introducing Jet-A into a high-compression reciprocating engine will rapidly induce severe, catastrophic detonation, leading to total engine failure shortly after takeoff.
* **Ignoring Oil Temperature Indications:** Treating high oil temperature solely as a cooling issue. A rising oil temperature combined with dropping oil pressure is the primary indication of an impending total engine failure due to an internal oil leak or bearing destruction.

### 4. Bridge Keys (Metadata)
* **Regs:** 14 CFR 91.205
* **Docs:** FAA-H-8083-25C Chapter 7
* **Keywords:** Pascal's Law, Hydrostatic Pressure, Stoichiometric, Viscosity, Condensation, 100LL, Jet-A
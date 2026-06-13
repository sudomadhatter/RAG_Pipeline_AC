### PA.VII.B.K1: Aerodynamics associated with stalls in various airplane configurations.

#### 1. The Oral Standard (The Direct Answer)
An aerodynamic stall occurs strictly when the wing exceeds its critical angle of attack (AOA), resulting in the separation of the boundary layer from the upper surface of the wing. While the wing continues to produce some lift during a stall, it can no longer generate adequate lift to sustain level flight. Because a stall is exclusively a function of exceeding the critical AOA, an aircraft can stall at any airspeed, any attitude, and any power setting.

#### 2. The Expert Deep Dive (The "Textbook")
**Regulatory Basis:** 14 CFR 23.2150 (formerly 23.201) dictates the certification requirements for stall behavior and characteristics.

**The "Why":** Boundary layer physics dictate that air can only travel against an adverse pressure gradient for a limited geometric angle before kinetic energy fails.

**Scenario Application:** A pilot attempts to forcefully pull the aircraft off the runway during a short-field takeoff before reaching rotation speed, stalling the wing while the nose is pointed sharply upward.

**The Mechanics of Boundary Layer Separation**
To comprehensively understand an aerodynamic stall, one must analyze the microscopic boundary layer—the viscous layer of air molecules adhering directly to the surface of the airfoil. As air flows over the curved upper surface of a wing, it accelerates. According to Bernoulli's Principle, this acceleration causes a decrease in static pressure, which generates the vast majority of the wing's lift vector.

As the AOA increases, the air must navigate over a steeper geometric curve. The coefficient of lift ($C_L$) increases almost linearly with the AOA up to a certain threshold. However, the air moving over the top of the wing eventually encounters an "adverse pressure gradient"—it must flow from the extreme low-pressure area at the peak of the camber back into the higher ambient atmospheric pressure toward the trailing edge. At high AOAs, the kinetic energy of the boundary layer is insufficient to push through this adverse pressure gradient. The boundary layer slows down, halts, and eventually reverses direction, tearing away from the surface of the wing.

This point of boundary layer separation defines the stall. The specific angle at which this separation universally occurs is the Critical Angle of Attack ($C_{L-MAX}$), which for most general aviation airfoils is between 15 and 20 degrees. Once the critical AOA is exceeded, the smooth laminar flow shatters into chaotic, turbulent eddies. The lift coefficient drops precipitously, and the form drag of the wing spikes massively.

**The "Zero Lift" Misconception**
A pervasive and dangerous myth in aviation instruction is that a stalled wing produces *zero* lift. This is physically incorrect. If a stalled wing produced zero lift, the aircraft would accelerate downward in a ballistic freefall at exactly 1 G ($32.2 ft/s^2$). In reality, a stalled aircraft falls at a much slower rate. The wing is still deflecting air downward and generating aerodynamic force. The critical distinction is that the lift vector has degraded so severely that it is no longer equal to or greater than the weight vector. The aircraft cannot sustain level flight, but it is not dropping like a stone in a vacuum.

**Load Factor and Accelerated Stalls**
The regulatory requirement to understand that a stall can occur at "any airspeed or attitude" hinges entirely on the physics of load factor (G-loading). The published stall speed ($V_s$) in the Pilot's Operating Handbook is mathematically valid only for unaccelerated (1G) flight. In a steeply banked turn, or during an abrupt pitch-up maneuver, the wings must generate additional lift to support the increased effective weight (load factor) of the aircraft. To generate this extra lift, the AOA must be increased. Consequently, the wing reaches its critical AOA at a much higher airspeed than it would in level flight. This is the definition of an accelerated stall, a primary killer in low-altitude maneuvering. The mathematical relationship is expressed as: $V_{s(acc)} = V_s \times \sqrt{n}$, where $n$ is the load factor. In a 60-degree banked turn, the aircraft experiences 2 Gs of load factor. The stall speed increases by the square root of 2 (approximately 1.41), meaning an aircraft that normally stalls at 50 knots will stall at 70 knots in a 60-degree bank.

| Flight Condition | Load Factor (G) | Stall Speed Multiplier | Practical Example ($V_s$ = 50 knots) |
| :--- | :--- | :--- | :--- |
| **Level Flight** | 1.0 G | 1.00x | Stalls at 50 knots |
| **45-Degree Bank** | 1.4 G | 1.19x | Stalls at 59 knots |
| **60-Degree Bank** | 2.0 G | 1.41x | Stalls at 70 knots |
| **75-Degree Bank** | 3.8 G | 1.96x | Stalls at 98 knots |

#### 3. Common Errors & Gotchas
* **The Airspeed Myth:** Believing that an aircraft cannot stall if it is flying fast. Airspeed is merely a proxy for AOA in 1G flight; AOA is the sole dictating aerodynamic factor of a stall.
* **Center of Gravity Misunderstanding:** Failing to recognize that a forward CG increases the stall speed. A forward CG requires more tail-down force from the horizontal stabilizer, which increases the total effective weight the main wing must support, driving the critical AOA to be reached at a higher airspeed.

#### 4. Bridge Keys (Metadata)
* **Regs:** 14 CFR 23.2150
* **Docs:** FAA-H-8083-25C (PHAK), AC 61-67C
* **Keywords:** Critical Angle of Attack, CL-MAX, Boundary Layer Separation, Accelerated Stall, Adverse Pressure Gradient, Load Factor, Lift Equation.
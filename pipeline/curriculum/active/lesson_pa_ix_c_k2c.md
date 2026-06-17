### PA.IX.C.K2c: Pitot-static system malfunction.

#### 1. The Oral Standard (The Direct Answer)
The pitot-static system relies on undisturbed ambient air (static) and ram air (pitot) to accurately measure airspeed, altitude, and vertical speed. A blocked pitot tube solely affects the airspeed indicator, causing it to read zero (if the drain is open) or act like an altimeter (if the drain is closed). A blocked static port freezes the altimeter and VSI in place, and causes the airspeed indicator to read erroneously low in a climb and erroneously high in a descent.

#### 2. The Expert Deep Dive (The "Textbook")

##### A. Bernoulli's Principle and the Airspeed Indicator (ASI)
To understand malfunctions, one must intimately understand the physics of the ASI. Total Pressure (PT) is the sum of Static Pressure (PS) and Dynamic Pressure (q). The ASI is essentially a mechanical diaphragm that measures only dynamic pressure, governed by the equation:

q = PT - PS

Ram air from the pitot tube fills the inside of the diaphragm (PT), while ambient static air from the static port fills the casing around it (PS). If the pitot tube ram hole and drain hole freeze over (e.g., in icing conditions), the Total Pressure (PT) becomes trapped in the lines. If the aircraft climbs, the actual static pressure (PS) entering the casing drops. Because the formula is q = PT - PS, subtracting a smaller static pressure from a trapped, unchanging total pressure mathematically yields a larger dynamic pressure. Thus, the airspeed indicator will erroneously show the aircraft speeding up as it climbs, acting precisely like an altimeter.

##### B. The Blocked Static Port
A blockage of the static port (often due to wax, tape, or insect nests) is a more complex failure because it affects all three flight instruments. The altimeter, which simply reads pure static pressure, will trap the pressure of the specific altitude where the blockage occurred and freeze perfectly still, regardless of ensuing climbs or descents. The Vertical Speed Indicator (VSI), which measures the rate of change of static pressure via a calibrated leak, will slowly bleed out to zero and freeze there. 

The ASI will continue to function, but highly inaccurately. It is now comparing incoming dynamic pitot pressure against the trapped static pressure from a different altitude. If the aircraft climbs above the blockage altitude, the trapped static pressure is artificially high compared to the actual outside air. Thus, the ASI will read erroneously lower than the actual airspeed, potentially leading the pilot to lower the nose and enter a dangerous dive to "gain speed".

##### C. The Alternate Static Source
To mitigate a completely blocked static port, most aircraft feature an Alternate Static Source valve. Opening this valve allows the instruments to draw static air from inside the unpressurized cabin. However, due to the aerodynamic venturi effect of air flowing rapidly over the fuselage, the air pressure inside the cabin is slightly lower than the undisturbed outside air. This lower pressure tricks the instruments: the altimeter will instantly jump and read slightly higher than actual, the VSI will momentarily show a climb, and the ASI will read slightly faster than actual airspeed.

| Malfunction Type | Airspeed Indicator (ASI) | Altimeter | Vertical Speed Indicator (VSI) |
| :--- | :--- | :--- | :--- |
| **Pitot Blocked (Drain Open)** | Drops to Zero | Normal | Normal |
| **Pitot Blocked (Drain Closed)** | Acts as an Altimeter (Increases in climb) | Normal | Normal |
| **Static Port Blocked** | Reads Low in Climb, High in Descent | Freezes at Blockage Altitude | Freezes at Zero |
| **Alternate Static Open** | Reads slightly Higher than actual | Reads slightly Higher than actual | Momentary climb, then Normal |

#### 3. Common Errors & Gotchas
* **The "Speeding Up" Illusion**: A pilot entering a cloud encounters pitot icing. As they pull back on the yoke to climb, they see the airspeed indicator increasing. They instinctively pull back harder to slow down, eventually stalling the aircraft because the ASI is acting as an altimeter.
* **Failing to Break the Glass**: If an aircraft lacks an alternate static source, and the static port is blocked, the emergency procedure requires the pilot to physically smash the glass face of the VSI to vent cabin air into the static system lines behind the panel.

#### 4. Bridge Keys (Metadata)
* **Regs**: 14 CFR 91.411
* **Docs**: FAA-H-8083-25C
* **Keywords**: Total Pressure, Dynamic Pressure, Static Pressure, Alternate Static Source, VSI, Bernoulli's Principle
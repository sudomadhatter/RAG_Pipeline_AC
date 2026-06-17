## PA.VI.B.R3: Limitations of the navigation system in use

### 1. The Oral Standard (The Direct Answer)
[cite_start]A safe and competent pilot understands that no single navigation system is infallible and plans their flight accordingly. [cite: 1519] [cite_start]Ground-based VOR systems are physically limited by line-of-sight signal degradation, terrain masking, and the cone of confusion directly above the station. [cite: 1520] [cite_start]Satellite navigation (GPS) is highly susceptible to intentional signal spoofing, solar flare interference, antenna shadowing during steep turns, and the unpredictable loss of RAIM integrity. [cite: 1521] [cite_start]Mitigating these inherent risks requires the pilot to continuously cross-check their primary navigation displays against secondary sources, such as pilotage or an independent VOR receiver. [cite: 1522]

### 2. The Expert Deep Dive (The "Textbook")

#### A. Inherent System Vulnerabilities and Physics
[cite_start]Rigorous risk management requires a proactive acknowledgment of physical system boundaries. [cite: 1525]
* [cite_start]**VHF Systems (VOR/LOC):** Because VORs rely on Very High Frequency radio waves, their propagation behaves similarly to light; [cite: 1526] they cannot penetrate solid objects. [cite_start]Mountainous terrain will effectively block the signal entirely (terrain masking). [cite: 1527] [cite_start]Furthermore, the VOR signal angular accuracy degrades with distance. [cite: 1528] [cite_start]A 1-degree error at 60 miles equates to being physically 1 mile off course. [cite: 1528]
* [cite_start]**GNSS/GPS:** The GPS constellation transmits incredibly weak radio signals from 12,000 miles in space. [cite: 1529] [cite_start]They are highly susceptible to Radio Frequency (RF) Interference. [cite: 1530] [cite_start]The military frequently conducts GPS jamming exercises (always noted via NOTAM) that can completely blackout civilian GPS receivers over hundreds of square miles. [cite: 1530] [cite_start]Furthermore, Multipath Error—where the satellite signal bounces off the aircraft wing or a nearby urban structure before hitting the antenna—can induce slight, unpredictable positional inaccuracies. [cite: 1531]

#### B. The Threat of Spoofing and RAIM Outages
[cite_start]While active signal jamming results in a clear "Loss of Signal" flag, Spoofing is a far more dangerous threat vector. [cite: 1532] [cite_start]Spoofing involves a malicious or experimental ground transmitter sending a fake GPS signal that gradually overpowers the authentic satellite signal. [cite: 1533] [cite_start]This slowly leads the aircraft's moving map astray without ever triggering an error flag or RAIM alert. [cite: 1534] [cite_start]Similarly, if the GPS constellation alignment shifts dynamically and the receiver loses visibility of five healthy satellites, it will suffer a RAIM Outage. [cite: 1534] [cite_start]Without RAIM, the receiver cannot guarantee the integrity of its positional solution. [cite: 1535] [cite_start]A pilot relying solely on GPS during a RAIM outage has absolutely no way of knowing if the magenta line is accurately depicting reality. [cite: 1536]

#### C. Mitigation via Correlation Navigation
[cite_start]To successfully manage these profound limitations, the pilot must employ "Correlation Navigation." [cite: 1538] [cite_start]This involves continuously verifying the primary system with an entirely independent data source. [cite: 1539] [cite_start]If the GPS indicates the aircraft is over a large lake, the pilot must look outside the window and verify the lake exists physically (pilotage). [cite: 1540] [cite_start]If the GPS is actively tracking a digital course, a standby VOR should be tuned to a nearby station to confirm the analog cross-radial lines up with the digital GPS position. [cite: 1541]

### 3. Common Errors & Gotchas
* [cite_start]**The Infallibility Assumption:** Treating the GPS moving map as the absolute truth. [cite: 1543] [cite_start]When the visual picture out the window completely contradicts the iPad or panel display, the pilot trusts the electronics over their own eyes, leading to severe disorientation. [cite: 1544]
* [cite_start]**Failure to Check NOTAMs:** Departing on a cross-country flight without reviewing specific GPS Interference NOTAMs, resulting in a total, unexpected loss of navigation capability mid-flight when traversing a military testing zone. [cite: 1545]
* [cite_start]**Ignoring the NAV Flag:** A VOR signal becomes too weak, and the TO/FROM flag disappears, replaced by a red NAV or OFF flag. [cite: 1546] [cite_start]The pilot continues to chase the frozen, unresponsive CDI needle, flying aimlessly off-course. [cite: 1547]

### 4. Bridge Keys (Metadata)
* [cite_start]**Regs:** 14 CFR 91.103 [cite: 1549]
* [cite_start]**Docs:** AIM 1-1-19, FAA-H-8083-25C [cite: 1550]
* [cite_start]**Keywords:** Line of Sight, Terrain Masking, Spoofing, GPS Jamming, RAIM Outage, Correlation Navigation [cite: 1551]
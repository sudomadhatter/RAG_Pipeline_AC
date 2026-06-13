## PA.I.C.K4: Flight deck instrument displays of digital weather and aeronautical information.

### 1. The Oral Standard (The Direct Answer)
Flight deck displays of digital weather, primarily utilizing ADS-B (FIS-B) or commercial satellite links like SiriusXM, provide pilots with weather graphics and aeronautical data overlaid on a moving map. While invaluable for strategic route planning and broad situational awareness, these systems possess inherent data latency. Pilots must understand that the weather depicted on the screen is delayed and must never be used for tactical weather penetration or close-quarters thunderstorm avoidance.

### 2. The Expert Deep Dive (The "Textbook")
**Regulatory Basis:** AC 00-63B (Use of Cockpit Displays of Digital Weather and Aeronautical Information). This AC provides guidance to flightcrew members on the best practices for the use of data link to access Flight Information Services (FIS).

**The "Why":** The modernization of the National Airspace System brought data-link weather directly into the cockpit to support the Next Generation Air Transportation System (NextGen) concepts of information sharing.  There are two primary architectural frameworks pilots interact with:
* **FIS-B (Flight Information Service-Broadcast):** A free, ground-based broadcast service provided by the FAA through the ADS-B Universal Access Transceiver (UAT) network operating on the 978 MHz frequency. Because it is ground-based, FIS-B is subject to line-of-sight limitations; aircraft operating at low altitudes or in mountainous terrain may lose the signal and cease receiving updates.
* **SiriusXM Aviation:** A paid, commercial non-FAA FIS system that utilizes S-band satellite broadcasting. Because the signal originates from space, there are virtually no altitude or line-of-sight limitations, allowing a pilot to receive national weather radar while sitting on the ramp with the engine off. Furthermore, SiriusXM often provides higher spatial resolution for specific products, such as freezing level graphics, compared to the broader, lower-resolution G-AIRMET data transmitted over FIS-B.

**The Latency Trap (NEXRAD):** The most critical limitation of in-cockpit weather is data latency. The "timestamp" or "age indicator" displayed on the iPad or Multi-Function Display (MFD) merely shows the age of the mosaic image created by the service provider, not the actual age of the weather conditions in the atmosphere. According to the National Transportation Safety Board (NTSB), it takes 5 to 6 minutes for a NEXRAD ground station to complete a 360-degree volumetric scan, and several more minutes to process, stitch, and transmit the mosaic image to the cockpit. Therefore, the radar return displayed in the cockpit can easily represent atmospheric conditions that are 15 to 20 minutes old.

**Scenario Application:** A pilot flying cross-country approaches a line of convective cells. Their FIS-B radar shows a 5-mile gap between two heavy red cells. The pilot attempts to use the display to fly tactically through the gap. Because of the 15-minute data latency and the fact that thunderstorms can grow at thousands of feet per minute, the gap has already closed in reality. The pilot inadvertently flies into a severe thunderstorm, risking airframe overstress and loss of control. The correct application is to use the datalink weather from 100 miles away to make a strategic decision to divert around the entire convective system entirely.

### 3. Common Errors & Gotchas
* **The Tactical Penetration Error:** Using NEXRAD to "thread the needle" between active thunderstorms. AC 00-63B dictates that datalink weather is for *strategic* avoidance (long-range decision-making) only, never for tactical (short-range) maneuvering.
* **Assuming Universal Coverage:** Expecting FIS-B weather to load while parked on the ramp at a mountain airport. 978 MHz UAT signals cannot pass through solid rock; coverage requires direct line-of-sight to the ADS-B ground tower.

### 4. Bridge Keys (Metadata)
* **Regs:** 14 CFR 91.103
* **Docs:** AC 00-63B, AIM 7-1-11
* **Keywords:** FIS-B, ADS-B, SiriusXM, NEXRAD Latency, Strategic vs. Tactical, UAT 978, Datalink Weather.
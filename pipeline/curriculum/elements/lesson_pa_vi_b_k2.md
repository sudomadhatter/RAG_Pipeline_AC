## PA.VI.B.K2: Satellite-based navigation

### 1. The Oral Standard (The Direct Answer)
[cite_start]Satellite-based navigation utilizes the Global Positioning System (GPS), which computes a precise three-dimensional position via trilateration from a constellation of orbiting satellites. [cite: 1356] [cite_start]A minimum of four satellites is necessary for a 3D navigational fix, five are required for Receiver Autonomous Integrity Monitoring (RAIM) to detect a faulty satellite signal, and six are required for fault exclusion. [cite: 1357] [cite_start]For VFR flight, navigating with an expired GPS database is legally permissible if the pilot manually verifies all waypoints against current aeronautical charts; [cite: 1358] [cite_start]however, rigorous risk management dictates maintaining current databases to prevent airspace deviations. [cite: 1359]

### 2. The Expert Deep Dive (The "Textbook")

#### A. Concept of Operation (The Mechanics of Trilateration)
[cite_start]GPS receivers calculate the aircraft's position by measuring the precise time it takes for a coded radio signal to travel from a satellite to the receiver antenna. [cite: 1360] [cite_start]Because the speed of light is a known constant, this time delay translates directly into a distance measurement, a process known as pseudo-ranging. [cite: 1361] [cite_start]The receiver mathematically intersects these distance spheres in a geometric process known as trilateration. [cite: 1362] [cite_start]Gathering signals from three satellites provides a basic two-dimensional fix (latitude and longitude). [cite: 1363] [cite_start]A fourth satellite is mathematically required to resolve the receiver's clock synchronization error, providing a complete 3D fix that includes geometric altitude. [cite: 1364]

#### B. Integrity Monitoring: RAIM and WAAS Architecture
[cite_start]A profound vulnerability of standard GPS is that an erroneous satellite signal can corrupt the navigation solution without triggering a system failure flag. [cite: 1365] [cite_start]Receiver Autonomous Integrity Monitoring (RAIM) is an internal algorithm designed to protect against this. [cite: 1366] [cite_start]RAIM requires a minimum of five satellites with adequate geometry to cross-check the signals and alert the pilot if one is transmitting corrupted data (Fault Detection). [cite: 1367] [cite_start]If a sixth satellite is visible, the receiver can automatically isolate and eliminate the bad signal entirely from the navigation solution (Fault Exclusion). [cite: 1368]

[cite_start]To achieve extreme precision and integrity, the FAA developed the Wide Area Augmentation System (WAAS). [cite: 1369] [cite_start]WAAS utilizes a network of ground-based Wide Area Reference Stations to measure minute ionospheric delays and satellite clock errors. [cite: 1370] [cite_start]These error corrections are transmitted to master stations, uplinked to geostationating satellites, and then beamed directly back down to the WAAS-capable aircraft receiver. [cite: 1371] [cite_start]This continuous, real-time error correction provides extraordinary accuracy and effectively eliminates the need for the pilot to manually perform RAIM predictions prior to flight. [cite: 1372]

| System Capability | Minimum Satellites Required | Primary Function |
| :--- | :--- | :--- |
| 2D Position Fix | 3 Satellites | Latitude and Longitude only. |
| 3D Position Fix | 4 Satellites | Latitude, Longitude, and Altitude. |
| RAIM (Fault Detection) | 5 Satellites | Detects a corrupted signal and alerts the pilot. |
| RAIM (Fault Exclusion) | 6 Satellites | Detects, isolates, and removes the corrupted signal. |

#### C. Database Currency and Regulatory Distinctions
[cite_start]The regulatory requirements governing GPS databases frequently generate operational confusion. [cite: 1374] [cite_start]According to the Aeronautical Information Manual (AIM 1-1-17) and Advisory Circular 90-100A, onboard navigation databases must be strictly current for any IFR operations. [cite: 1375] [cite_start]Conversely, the FAA does not explicitly require database currency for VFR operations. [cite: 1375] [cite_start]The AIM stipulates that pilots utilizing an outdated database for VFR flight must verify their intended waypoints using current aeronautical products (such as a valid Sectional Chart or Chart Supplement). [cite: 1376] [cite_start]Despite this legal allowance, the expert standard dictates that relying on expired electronic data in highly dynamic, shifting airspace architectures represents a profound failure in risk management. [cite: 1376]

### 3. Common Errors & Gotchas
* [cite_start]**The Handheld Illusion:** Pilots utilizing VFR-only panel mounts or handheld consumer tablets (such as an iPad running ForeFlight) must understand that these devices inherently lack RAIM capability. [cite: 1378] [cite_start]They cannot alert the pilot to a deteriorating navigation solution, signal degradation, or active spoofing, making them legally and practically suitable only for situational awareness, never primary navigation. [cite: 1379]
* [cite_start]**Altitude Confusion:** GPS altitude is calculated based on geometric height above an artificial ellipsoid model of the Earth (WGS-84), which differs significantly from the barometric altitude (Mean Sea Level) required by 14 CFR 91.121 for standard aircraft vertical separation. [cite: 1380] [cite_start]Pilots must navigate vertically using the certified barometric altimeter, not the GPS altitude readout. [cite: 1381]
* [cite_start]**The VFR Database Assumption:** A pilot operating under VFR assumes that the expired database on their legacy Garmin 430 is "close enough" without cross-referencing a physical terminal chart, inadvertently flying into a newly established restricted area or altered Class B shelf that the outdated system does not depict. [cite: 1382]

### 4. Bridge Keys (Metadata)
* [cite_start]**Regs:** 14 CFR 91.121, 14 CFR 91.205 [cite: 1384]
* [cite_start]**Docs:** AIM 1-1-17, AC 90-100A, FAA-H-8083-25C [cite: 1385]
* [cite_start]**Keywords:** Global Positioning System, RAIM, Trilateration, Fault Detection, Fault Exclusion, Wide Area Augmentation System, Database Currency [cite: 1386]
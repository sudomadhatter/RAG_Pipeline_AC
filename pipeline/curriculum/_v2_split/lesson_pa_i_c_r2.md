## PA.I.C.R2: Use and limitations of aviation weather equipment and resources.

### 1. The Oral Standard (The Direct Answer)
Effective risk management requires the understanding that no single weather product is infallible. Installed onboard equipment suffers from significant data latency, rendering it unsuitable for tactical weather penetration. Aviation forecasts, such as TAFs, are highly accurate but geographically restricted to the immediate airport vicinity. Inflight resources rely on radio line-of-sight and controller workload, meaning pilots must proactively cross-reference multiple data streams to maintain an accurate mental model of the atmosphere.

### 2. The Expert Deep Dive (The "Textbook")
**Regulatory Basis:** AC 00-63B and AIM Chapter 7.

**The "Why":**
* **Onboard Weather Equipment (R2a):** As highlighted by the NTSB, even small time differences between the age indicator on an MFD and actual atmospheric conditions can be fatal when considering fast-moving weather hazards. A pilot viewing a FIS-B screen might see a "clear" area that is actually filled with a developing microburst, because the radar sweep is 15 minutes old and the convection is building at thousands of feet per minute. Always verify the currency of radar imagery, avoiding old or mosaic data for tactical navigation.
* **Reports and Forecasts (R2b):** The Terminal Aerodrome Forecast (TAF) is a micro-forecast. It applies strictly to a 5-Statute-Mile radius around the airport complex. Pilots traversing a 100-mile route between two TAF-reporting airports must not assume the weather between them interpolates linearly. They must use the Graphical Forecasts for Aviation (GFA) to assess the 90 miles of airspace not covered by the TAFs. Additionally, METARs only report what is directly over the optical sensors; a massive thunderstorm 10 miles off the end of the runway will not appear in the primary sky cover group of the METAR.
* **Inflight Weather Resources (R2c):** Pilots must transition from ground-based preflight planning to inflight updates when conditions change. However, inflight resources rely on VHF radio line-of-sight. At low altitudes, terrain masking may prevent a pilot from contacting Flight Service or ATC to get critical updates, leading to a loss of situational awareness.

**Scenario Application:** A pilot departs under a clear sky based on a pristine TAF at the departure and destination airports. En route, they notice a dark wall of clouds ahead with virga trailing beneath it. Recognizing the limitation that TAFs do not cover the en route airspace, and understanding that their onboard FIS-B radar has a 15-minute latency, they immediately tune to the nearest FSS frequency found on the sectional chart to request an in-flight update. They discover an unforecast pop-up squall line and execute a timely diversion.

### 3. Common Errors & Gotchas
* **The "Clear METAR" Assumption:** Seeing "CLR" on a METAR and assuming the sky is entirely blue. Automated stations (ASOS) only look straight up and typically only detect clouds up to 12,000 feet. There could be an overcast layer at 15,000 feet, or severe weather just outside the sensor's narrow field of view.
* **Misinterpreting Radar Age:** Looking at the "Time: 14:02Z" on an iPad and believing the radar picture reflects the sky at exactly 14:02Z. That is the broadcast time of the mosaic, not the atmospheric scanning time.

### 4. Bridge Keys (Metadata)
* **Regs:** 14 CFR 91.103
* **Docs:** AC 00-63B, AIM 7-1, FAA-H-8083-28
* **Keywords:** Radar Latency, TAF 5SM Limit, ASOS Limitations, Inflight Weather Resources, FIS-B, NEXRAD.
# Lesson 11: Reading & Decoding METARs and SPECIs
## PPL_PA_I_C_02 | ACS Elements: PA.I.C.K2, PA.I.C.K2a

### What This Lesson Covers
The DPE will hand you a METAR and ask you to decode it live. Every element has a trap: wind is TRUE not magnetic, cloud heights are AGL not MSL, CLR and SKC mean different things, and the first BKN or OVC layer — not the first cloud — defines the ceiling.

### The Four Knowledge Points

**RKP_01: The Eight METAR Elements**
Type → Station ID (ICAO) → Date/Time (DDHHMMZ Zulu) → Wind (True degrees, knots) → Visibility (statute miles) → Present Weather (RA, SN, FG, BR, TS, HZ) → Sky Condition (height in hundreds of feet AGL) → Temp/Dew (°C, M prefix for minus) → Altimeter (A_ _ _ _).

**RKP_02: Wind Direction Is True — NOT Magnetic**
Text METARs and TAFs report wind direction in TRUE degrees. ASOS/AWOS voice broadcasts and ATIS convert to magnetic for runway alignment. When you hear an ATIS, that's magnetic. When you read a METAR text string, that's true. Apply your local magnetic variation to convert for heading accuracy. Winds Aloft (FB) are also true.

**RKP_03: Sky Condition Heights Are AGL — Always**
BKN045 = broken clouds at 4,500 feet ABOVE GROUND LEVEL. Not MSL. Say AGL every time the DPE asks.

How to find the ceiling: the ceiling is the LOWEST BKN or OVC layer. FEW and SCT layers are not ceilings. A METAR reading FEW015 SCT030 BKN070 has a ceiling at 7,000 feet AGL.

Flight category thresholds to memorize:
- VFR: above 3,000 AGL AND above 5SM visibility
- MVFR: 1,000–3,000 AGL OR 3–5SM visibility  
- IFR: 500–999 AGL OR 1–3SM
- LIFR: below 500 AGL OR below 1SM

**RKP_04: SPECI — Off-Cycle Special Report**
A SPECI fires when conditions change rapidly between hourly METARs. Trigger conditions include: thunderstorm onset/cessation, tornado/funnel cloud, visibility crossing through VFR/MVFR/IFR/LIFR thresholds, ceiling crossing 3,000/1,500/1,000/500 AGL thresholds, wind shift of 45°+ with new speed 10 knots or more. A pilot who checks a routine 0900Z METAR and departs at 0855Z as conditions were rapidly changing may have no SPECI available yet — SPECIs look backward in real-time, not forward.

### Key Regulations
- 14 CFR 91.103 — Requires obtaining weather including current conditions (METARs)
- 14 CFR 91.155 — VFR weather minimums (flight category thresholds)
- AC 00-45H — Aviation Weather Services (the authoritative METAR/TAF decode reference)
# Lesson 16: Navigation Math — TAS, Groundspeed, Headings, Time/Distance/Fuel
## PPL_PA_I_D_02 | ACS Elements: PA.I.D.K3a, PA.I.D.K3b, PA.I.D.K3c

### What This Lesson Covers
The four essential nav-math skills: the TC → TH → MH → CH heading sequence with the East/West variation rule, why TAS is always higher than IAS at altitude, UTC time conversion and the Daylight Saving Time trap, and fuel requirements — why the FAA's 30-minute minimum is a floor, not a target.

### The Four Knowledge Points

**RKP_01: The Four-Step Heading Sequence**
True Course (TC) → ± Wind Correction Angle → True Heading (TH)
→ ± Magnetic Variation → Magnetic Heading (MH)
→ ± Compass Deviation → Compass Heading (CH)

Variation rule: East is Least (subtract), West is Best (add).
East = subtract variation from TH to get MH.
West = add variation to TH to get MH.

The DPE gives you a TC and asks for CH. Don't skip steps. Don't confuse heading with course.

**RKP_02: TAS and Groundspeed**
IAS = what the indicator shows.
TAS = actual speed through the airmass. At altitude, TAS > IAS by about 2% per 1,000 feet.
At 8,000 feet, an IAS of 110 knots = TAS of approximately 128 knots.
GS = TAS ± wind (+ tailwind, − headwind).

All navlog ETE calculations use GROUNDSPEED, not TAS, not IAS.
ETE = Distance ÷ Groundspeed.

**RKP_03: UTC Conversion and the DST Trap**
Aviation uses Zulu time (UTC) universally.
Converting local to UTC: ADD the offset. UTC to local: SUBTRACT.
Eastern: +5 standard / +4 daylight saving.
Central: +6 standard / +5 daylight saving.
Mountain: +7 standard / +6 daylight saving.
Pacific: +8 standard / +7 daylight saving.

The DST trap: in summer, Eastern is UTC-4, not UTC-5. One hour error = wrong ETA = potential SAR trigger.
Math trap: time is base-60. 0.5 hr = 30 min, not 50 min.

**RKP_04: Fuel Requirements — Legal vs. Professional**
14 CFR 91.151: Carry enough fuel to fly to the destination + 30 more minutes (day) or 45 minutes (night) at normal cruise. This is the LEGAL FLOOR.
Professional minimum: 1 hour reserve.
Fuel gauge reliability: 14 CFR 23.1337 only requires accuracy at zero (empty). All other readings are approximations. USE A DIPSTICK at preflight.

Fuel planning order: startup/taxi (1–1.5 gal) + climb (use POH chart) + cruise (ETE × GPH, leaned) + reserve.

### Key Regulations
- 14 CFR 91.151 — Fuel requirements (30-day / 45-night reserve minimum)
- 14 CFR 91.153 — VFR flight plan times must be in UTC
- 14 CFR 23.1337 — Fuel gauge accuracy: required only at zero
- 14 CFR 91.103 — Preflight action (fuel planning is a legal requirement)
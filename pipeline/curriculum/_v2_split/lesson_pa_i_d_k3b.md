## PA.I.D.K3b: Calculating: Estimated time of arrival, including conversion to universal coordinated time (UTC)

### 1. The Oral Standard (The Direct Answer)
Estimated Time of Arrival (ETA) is calculated by dividing the total distance of the route by the calculated groundspeed to find the estimated time en route (ETE), and then adding that duration to the proposed departure time. To convert local time to Universal Coordinated Time (UTC, commonly referred to as Zulu time), the pilot must apply the appropriate geographic time zone offset, taking care to account for Daylight Saving Time if it is currently in effect.

### 2. The Expert Deep Dive (The "Textbook")
**Regulatory Basis:** 14 CFR 91.153 requires the proposed time of departure and the estimated elapsed time until over the destination to be included on a formal VFR flight plan.28 These plans are processed entirely in UTC to eliminate dangerous time zone confusion across the National Airspace System.

**The "Why":** Aviation operates on a global standard—Zulu time—to ensure flawless synchronization between Air Traffic Control, weather forecasts (such as TAFs and METARs), and pilots who may be crossing multiple time zones in a single flight.5 The ETA is a highly dynamic variable; it is initially calculated on the ground, but it must be continuously recalculated in the air using the actual time flown between checkpoints.27 This updating process verifies if the initial groundspeed and wind predictions were accurate and ensures the pilot can alert Flight Service if their arrival will be delayed past their search and rescue window.29

| US Time Zone | Standard Time Offset (Winter) | Daylight Saving Time Offset (Summer) |
| :--- | :--- | :--- |
| Eastern (EST/EDT) | UTC - 5 hours | UTC - 4 hours |
| Central (CST/CDT) | UTC - 6 hours | UTC - 5 hours |
| Mountain (MST/MDT) | UTC - 7 hours | UTC - 6 hours |
| Pacific (PST/PDT) | UTC - 8 hours | UTC - 7 hours |

**Scenario Application:** A pilot in Florida (Eastern Time) plans a flight with a 2-hour En Route Time (ETE). The departure time is 14:00 Local during Standard Time. Eastern Standard Time requires adding 5 hours to convert to Zulu. Therefore, departure is 19:00 Zulu. Adding the 2-hour ETE, the exact ETA is 21:00 Zulu. If the pilot arrives at their first en route checkpoint 2 minutes late due to an unexpectedly strong headwind, they must extrapolate that delay across the remaining route distance to generate an updated, realistic ETA for ATC and their own fuel management plan.27

### 3. Common Errors & Gotchas
* **Forgetting Daylight Saving Time:** Failing to adjust the UTC conversion factor during Daylight Saving Time (e.g., assuming Eastern Time is always -5, when it changes to -4 during the summer months).
* **Math errors with base-60:** Calculating time in decimal hours (e.g., 1.5 hours) but erroneously treating it as 1 hour and 50 minutes instead of 1 hour and 30 minutes when adding the duration to a clock time.24

### 4. Bridge Keys (Metadata)
* **Regs:** 14 CFR 91.153
* **Docs:** FAA-H-8083-25 (PHAK Ch 16), AIM 4-2-12
* **Keywords:** UTC, Zulu Time, ETA, ETE, Time Zones, Base 60 Math

---
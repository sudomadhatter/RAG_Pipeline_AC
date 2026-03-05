## PA.I.F.S1: Compute the weight and balance, correct out-of-CG loading errors and determine if the weight and balance remains within limits during all phases of flight.

### 1. The Oral Standard (The Direct Answer)
The applicant must demonstrate the physical skill to mathematically calculate the aircraft's Center of Gravity for both the takeoff and landing phases, utilizing the specific aircraft's actual Basic Empty Weight documentation. If the initial calculation places the CG outside the legal envelope, the applicant must use the weight-shift formula to determine exactly how much weight to move, or add/remove, to bring the aircraft safely back into limits, ensuring stability throughout the entire flight.

### 2. The Expert Deep Dive (The "Textbook")

**Regulatory Basis:** Practical compliance with **14 CFR 91.9(a)** requires the PIC to mathematically prove, via written or digital record, that the aircraft is loaded within the precise limits prescribed in the specific aircraft's AFM before the engine is started.

**The "Why":** Weight and balance is an exercise in managing physical torque, referred to in aviation as "moments." The fundamental physics equation governing this process is Weight x Arm = Moment. By tabulating all individual weights and their respective moments, and dividing the Total Moment by the Total Weight, the pilot discovers the exact Center of Gravity (the Total Arm).
* **The In-Flight Shift:** The Center of Gravity is not a static point; it moves during flight. As fuel combusts, weight is continuously removed from the aircraft. If the fuel tanks are located slightly aft of the CG (a common trait in high-wing Cessnas), burning fuel removes weight from the rear, causing the seesaw to tip forward, and the CG marches progressively forward as the flight continues. A pilot who takes off precisely on the forward limit line will arrive at their destination two hours later illegally and dangerously out of bounds, risking a wheelbarrowing accident upon landing.
* **The FATCAT Formula:** To correct an out-of-balance aircraft without erasing and re-doing the entire mathematical spreadsheet, pilots use the weight shift formula. The formula dictates that the change in Center of Gravity ($\Delta CG$) is equal to the weight shifted, multiplied by the distance it was shifted, divided by the total weight of the aircraft:

$$\Delta CG = \frac{WeightShifted \times DistanceShifted}{TotalWeight}$$

**Scenario Application:** The pilot calculates their loaded takeoff weight to be 2,500 lbs. The total CG is calculated at 44.0 inches aft of the datum. Checking the POH envelope, the absolute aft limit is 43.5 inches. The aircraft is 0.5 inches too far aft and is therefore unairworthy. The pilot realizes they need to move heavy baggage from Area 2 (Arm: 150") to Area 1 (Arm: 110") behind the front seats. The physical distance between the two stations is 40 inches. Using the formula: 0.5 = (Weight Shifted x 40) / 2500. Solving algebraically for Weight Shifted: (0.5 x 2500) / 40 = 31.25 lbs. By physically moving exactly 31.25 lbs of baggage from Area 2 to Area 1, the CG moves exactly 0.5 inches forward to the legal limit of 43.5 inches, making the flight safe and legal.

### 3. Common Errors & Gotchas
* **Math Errors in the Shift Formula:** A frequent checkride failure involves mixing up the variables in the weight shift formula—specifically confusing the "Distance Shifted" (the physical inches between the two baggage compartments, e.g., 40 inches) with the actual Arm of a single compartment (e.g., 150 inches).
* **The Zero-Fuel Calculation Miss:** Failing to calculate the landing CG. An examiner will almost always create a scenario specifically designed to push the CG slowly out of limits during a 4-hour cross-country flight due solely to fuel burn.
* **Using Oil as a Variable:** Forgetting that in modern General Aviation aircraft, the official Basic Empty Weight usually *includes* full operating fluids, including full engine oil. Adding the weight of oil again in the calculation throws off the math and demonstrates a lack of understanding of the aircraft's documentation.

### 4. Bridge Keys (Metadata)
* **Regs:** 14 CFR 91.9
* **Docs:** FAA-H-8083-1B (W&B Handbook Ch 4 & Ch 10)
* **Keywords:** $\Delta CG$, FATCAT, Weight Shift Formula, Moment, Zero Fuel Weight, In-Flight CG Shift, Arm, Datum.

---
# CLOAK Campaign Simulator — Owner Input Needed

We're building a Monte Carlo simulator to model the IndieGoGo campaign
and help decide: what goal to set, how much to invest in pre-launch
marketing, and whether to hire an agency like LaunchBoom.

The simulator is calibrated against 14,648 real Kickstarter campaigns.
To make it useful for CLOAK specifically, we need the following inputs.

---

## Must-Have (blocks the model)

### 1. Bill of Materials — true cost per unit
Current placeholder: $45 COGS + $12 shipping = $57/unit.
What's the real number?

- Material cost per cover: $___
- Labor cost per cover: $___
- Packaging: $___
- **Total COGS per unit: $___**

### 2. Shipping cost per unit
- Domestic (US): $___
- International (if offered): $___
- Flat rate or varies by destination?

### 3. Tooling / upfront costs already invested
This is a natural anchor for the funding goal — "we spent $X on
tooling, let's recoup it."

- Total tooling investment to date: $___
- Any other sunk costs (prototyping, certifications, etc.): $___

### 4. Production capacity
We have 20/day. Confirming:

- Units per day at steady state: ___
- Ramp-up time (days before hitting steady state): ___
- Minimum batch size (if any): ___
- Maximum you'd want to commit to fulfilling from one campaign: ___

### 5. What does "success" look like?
Not the funding goal — the business outcome.

- Minimum pre-orders to make the campaign worthwhile: ___
- Dream scenario (units): ___
- Is this purely pre-orders, or also validation / marketing / awareness?

---

## Strategy Questions

### 6. Pre-launch budget
How much are you willing to spend *before* launch on audience-building
(ads, email list, content, agency)?

- $0 (organic only)
- $1,000 - $3,000
- $3,000 - $8,000
- $8,000 - $15,000 (LaunchBoom range)
- Other: $___

### 7. Timeline
- Earliest you could launch: ___
- How many weeks/months of pre-launch prep are you willing to do: ___

### 8. LaunchBoom / agency interest
LaunchBoom charges $4K-$12K + ad spend. Their $1 reservation funnel
converts at 35-45% vs 5-10% for a regular email list. Worth exploring?

- Yes, interested
- Maybe, depends on the ROI numbers
- No, DIY only

### 9. Pricing confirmation
- Standard price: $200 (confirmed)
- Early bird price: $149.99 — is this right?
- Early bird quantity (how many at the discount): ___
- Any other tiers planned (e.g., 2-pack, family pack)?

### 10. Stretch goals
Any planned? These affect revenue ceiling modeling.

- None
- Yes (describe): ___

---

## Nice to Know

### 11. Fulfillment plan
- Ship yourself
- Use a 3PL (which one?)
- Haven't decided yet

### 12. Platform preference
- IndieGoGo (current assumption)
- Kickstarter
- BackerKit Launch
- Open to whichever the model says is best

---

Once we have answers to 1-5, the simulator can produce actionable
recommendations for goal, budget allocation, and expected outcomes.

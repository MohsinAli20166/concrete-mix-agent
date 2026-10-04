# Product Requirements Document — ConcreteAI SitePlan

## Problem and audience

Small contractors and junior site engineers need to convert a concrete material estimate into an actionable purchase list. They must account for stock already on site, material prices, bag sizes and a remaining purchase budget. ConcreteAI SitePlan extends the earlier mix prototype to cover this planning step.

Primary users: site supervisors, small contractors, trainees and students. The prototype is intended for preliminary planning and demonstration, not final mix approval.

## Product goal

From a confirmed mix, dimensions, stock and prices, produce a transparent material purchase estimate with a downloadable CSV. Optional AI explains the result in English, Urdu or Roman Urdu.

## Functional requirements

1. Accept rectangular length/width in feet and thickness in inches.
2. Accept an optional 0–30% quantity allowance.
3. Accept an educational mix estimate or user-supplied mix quantities in kg/m³.
4. Accept cement bag weight and sand/aggregate bulk densities.
5. Calculate cement bags, bulk aggregate volumes in cft and water litres.
6. Deduct available stock, prevent negative purchases, and round cement shortages up to whole bags.
7. Accept user-entered PKR rates with explicit known/unknown status. A known zero rate represents a free supply.
8. Calculate remaining purchase costs and delivery, separately from full material value.
9. Compare only a complete purchase estimate with an optional remaining-purchase budget.
10. Export a UTF-8 CSV containing units, inputs, quantities, costs, assumptions and limitations.
11. Provide deterministic summaries in three languages.
12. Optionally use Claude tools over the confirmed form snapshot. Display actual calls. Handle API failure with a labelled deterministic fallback.
13. Mark AI answers stale when the source inputs, question, model or language change.

## Non-functional requirements

- Calculations run locally in Python and need no LLM.
- A hosted app requires network access; local calculation can run without internet after installation.
- Validate missing, negative, non-finite and unsupported numeric inputs.
- No API credentials in source, exports or calculation traces.
- AI service use occurs only on explicit button press and receives current project data.
- Show unknown costs as incomplete instead of silently assigning zero.
- Keep tool calls bounded to five response cycles; client timeout 30 seconds per request, no automatic SDK retries.
- No persistent database; form state lives in the Streamlit session, and users save CSVs themselves.

## Architecture

Streamlit collects confirmed inputs. The educational mix engine or user-supplied mix provides kg/m³. The deterministic planner scales quantities, converts purchasing units, subtracts stock and calculates costs. Streamlit displays the results and creates the CSV. Claude, when enabled, decides which read-only calculation tools to call and explains their returned data. Tool inputs are bound to the current form; the model cannot change the mix or budget.

Technology: Python 3.12, Streamlit 1.65.0, Anthropic SDK 1.11.0, Python standard-library CSV and unittest. Intended source hosting: GitHub; intended app hosting: Streamlit Community Cloud. Deployment remains the owner's action.

## Finance

- Material rates, stock, delivery and remaining budget are entered by the user. The system does not fetch live supplier prices.
- Procurement total includes listed material purchases and entered delivery only.
- Development time, hosting costs and API charges are not included in construction costs.
- Software operation costs depend on the selected hosting arrangement and Anthropic usage. No fixed or zero-cost hosting claim is assumed.
- Revenue is not implemented. A future business model could offer paid project history and report features; pricing and demand are unvalidated.

## Scope and limitations

Included: single rectangular concrete scope, preliminary mixes, purchase arithmetic, budget status, CSV and optional tool-based explanations.

Excluded: final structural design, verified exposure classification, engineer approval, live pricing, supplier ordering, payment, inventory database, moisture corrections, admixtures, reinforced-concrete design, comprehensive BOQ, measured savings or accuracy guarantees.

The inherited engineering constants and exposure presets are unverified demo assumptions. The strength table is bounded to 2000–5000 psi and interpolated. Bulk density assumptions are editable and do not replace material measurements. A provided project mix is not independently validated. Budget pressure never triggers strength or mix reduction.

## Acceptance and validation

- Known 1 m³ fixture matches hand-calculated bag and aggregate purchase quantities.
- Missing rate for a required purchase blocks total/budget assessment.
- Adequate stock needs no purchase; surplus produces no negative cost.
- A zero price is usable only as an explicitly entered price.
- CSV matches the calculation and neutralizes formula-like project names.
- Demo loads, budget warnings update, custom mix works, invalid dimensions show an error, and old assistant answers become stale.
- Seventeen automated tests passed at delivery, including mocked agent interactions. Live Anthropic access, owner deployment and engineering certification were not tested or completed.

## Team and links — complete before submission

- Team leader: [add actual name]
- Team members and individual contributions: [add actual information]
- App link: [add deployed URL]
- Code link: [add repository URL]
- Presentation link: [add slides URL]
- Demo video link: [add video URL]

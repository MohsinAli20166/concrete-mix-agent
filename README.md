# ConcreteAI SitePlan

**Know what to buy. Know the cost.**

PakAngel GenAI & Agentic AI Training Program — Cohort C11 final hackathon upgrade.

ConcreteAI SitePlan extends the earlier concrete mix prototype into a preliminary material cost and purchase planner for small contractors and site supervisors. Enter dimensions, a mix, available materials and local rates; get remaining purchases, estimated PKR costs, budget status and an Excel-compatible CSV.

## Run

Use Python 3.12. In this folder:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Click **Load demo project** in the sidebar. The sample rates and bulk densities are illustrative, not current supplier quotes or measured site data. All calculators and CSV downloads work without an API key. A locally installed app can calculate without internet; a hosted Streamlit app still requires internet to reach it.

See **START_HERE.md** for GitHub/Streamlit deployment and **DEMO_GUIDE.md** for the presentation walkthrough.

## What changed

| Earlier prototype | Final upgrade |
|---|---|
| Mix estimation and area quantities | Cost, stock shortages, budget comparison and CSV purchase list |
| Solid aggregate volumes labelled as site cft | Bulk purchase cft based on editable assumed bulk densities |
| A fixed 50 kg bag convention | Configurable bag weight; whole-bag purchase rounding after stock deduction |
| Unsupported code-compliance / automatic grade claims | Clearly labelled educational presets; user-supplied project mix option |
| A one-pass tool call | Bounded Claude tool loop, multiple tool-result handling and visible trace |
| Offline keyword inference described as an agent | Explicit deterministic offline summary; no simulated live AI |

## Features

- Rectangular quantity estimate: length and width in feet, thickness in inches.
- Optional quantity allowance; no automatic mix or strength reduction to meet budget.
- Educational absolute-volume mix estimate, or user-supplied project mix in kg/m³.
- Cement bags, bulk sand/aggregate cft, water litres.
- User-entered rates and stock; unknown rates are not treated as free.
- Full material value separated from remaining purchase costs.
- Optional remaining-purchase budget and delivery charges.
- English, Urdu and Roman Urdu deterministic summaries.
- UTF-8 CSV with assumptions, prices, quantities and budget status.
- Optional Claude tool-use with the current confirmed form snapshot. Chat does not edit the form.
- Stale AI answers are hidden when inputs or question change.

## AI configuration

The app reads `ANTHROPIC_API_KEY` and optional `ANTHROPIC_MODEL` from environment variables or Streamlit secrets. It also accepts a masked session-only key in the sidebar. Never put an API key in source code or GitHub.

The default model is `claude-haiku-4-5-20251001`; it is configurable. Claude is called only when the user clicks **Run live agent**. That sends the question and current project input data to Anthropic. API charges depend on usage and the connected account.

The agent can call `calculate_mix_design` and `calculate_purchase_plan`. Tools use the form snapshot and accept no overrides. Changed quantities or prices must be entered in the form first. The offline button summarizes the form and does not interpret free-text questions. If the API fails, the app labels the deterministic fallback clearly.

## Files

- `app.py`: Streamlit UI and form state.
- `mix_design_tool.py`: inherited educational method, bounded inputs and interpolated demo strength table.
- `purchase_planner.py`: deterministic quantities, costs, CSV and multilingual summaries.
- `agent.py`: Claude tool-use loop and trace.
- `tests/`: arithmetic, CSV, mocked agent and Streamlit AppTest checks.
- `PRD.md`: scope, requirements, architecture, costs and limitations.
- `DEMO_GUIDE.md`: reproducible demo and presentation outline.

## Validation

```bash
python -m unittest discover -s tests -v
```

The delivery was tested on Python 3.12 with Streamlit 1.65.0 and Anthropic Python SDK 1.11.0. Seventeen automated tests cover a hand-calculated fixture, bag rounding, bulk conversion, invalid inputs, missing and zero rates, surplus stock, budget status, CSV export, multilingual summaries, mocked agent tool calls and Streamlit flows.

Live Anthropic service access has not been tested with the owner's credentials. Engineering suitability and code compliance have not been validated. No deployment was performed as part of this ZIP delivery.

## Engineering limitations

This is a preliminary planning prototype, not construction approval. The educational exposure presets are inherited demo assumptions, not verified ACI exposure classes or PBC requirements. Calculated proportions do not guarantee achieved strength. Strength input is bounded to the demo table's 2000–5000 psi range.

The engine assumes material properties, air, water and coarse aggregate factors. No lab testing, target-average strength margin, moisture/absorption correction, admixture calculation, or code compliance verification is performed. A supplied project mix is also not independently checked. Lab trials and engineering review remain necessary.

Purchase volumes use **bulk density**, not aggregate specific gravity. Defaults require replacement with material-specific values. Bulk purchasing volumes are not field batching instructions. Water is a planning quantity, not a dosing instruction. The rectangular scope excludes beams, openings and irregular shapes. Costs exclude labour, equipment, taxes and unentered charges.

## References

- [ACI 211.1-22 preview: proportions are preliminary and need trial validation](https://www.concrete.org/Portals/0/Files/PDF/Previews/211.1-22_preview.pdf)
- [Anthropic tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Anthropic Haiku migration guide and model identifier](https://platform.claude.com/docs/en/models/haiku-4-5/migration-guide)

These references explain the method and API; they do not certify the inherited preset values used in this prototype.

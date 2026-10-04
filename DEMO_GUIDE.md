# ConcreteAI SitePlan — 4–5 minute presentation guide

Prepare six simple slides from the points below. Add actual team names and contributions. This file is an outline and narration guide; it is not a PowerPoint file or recorded video.

## 0:00–0:30 — Problem

“Small contractors need to know what materials to buy before a concrete pour. Knowing the mix is only one part. They also need to consider materials already available and the money still required.”

Slide: one problem sentence and three questions: How much is needed? What is already on site? What must we buy?

## 0:30–1:00 — What is new

“Our earlier project estimated a preliminary concrete mix. Our final upgrade, ConcreteAI SitePlan, adds material costs, stock deduction, budget comparison and a downloadable purchase list.”

Slide: Previous: mix + quantities. New: stock + purchase cost + budget + export. Do not present earlier work as newly built.

## 1:00–1:25 — How it works

“Python performs the calculations. Optional Claude tool-use reads the confirmed project inputs, calls the calculation tools and explains the returned results. Without the API, a clearly labelled deterministic summary still works.”

Slide: inputs → Python calculations → purchase plan → optional AI explanation.

## 1:25–3:35 — Live demo

1. Click **Load demo project**. State that all prices are illustrative.
2. Show 20 ft length, 15 ft width and 6 inch thickness: **150 cft**.
3. Show 5% quantity allowance: approximately **4.46 m³** for planning.
4. Show existing stock and prices. Point out that cement is priced per 50 kg bag.
5. Show remaining purchases plus delivery: approximately **PKR 42,845**. Budget remaining: approximately **PKR 7,155** against PKR 50,000.
6. Change the remaining purchase budget to **PKR 40,000**. It should flag a shortfall of approximately **PKR 2,845**.
7. Explain: “The app highlights the gap; it does not weaken the specified mix.”
8. Uncheck Cement's **Price entered** box. Show that the total becomes incomplete. Check it again.
9. Download the purchase CSV. Explain that it includes assumptions and quantities.
10. If you already verified your API key, use **AI assistant → Run live agent** with the default question. Show actual tool calls. Otherwise use **Show offline plan summary**, clearly stating that it is not live AI.

All PKR values above come from the shipped demo inputs, not market research or a supplier quotation. The 3000 psi demo estimate does not establish achieved strength.

## 3:35–4:05 — Validation and limits

“We tested purchase arithmetic, whole-bag rounding, missing prices, surplus stock, budget changes, CSV export and the app flow. This is a preliminary planning prototype. Material testing, moisture corrections and engineering review are still necessary.”

Slide: tested arithmetic and app flows; no code-compliance or final-design claim. Do not say the live API was verified until you have checked it with your own credentials.

## 4:05–4:45 — Team and close

State each actual member's contribution briefly. Show the app, repository and PRD links.

“Our next step is to validate the workflow with real site supervisors and supplier rates. ConcreteAI SitePlan helps users see what remains to purchase and what the entered prices imply for their budget.”

## Quick Roman Urdu explanation

“Pehle hamara project concrete mix ka ibtidai hisaab deta tha. Ab hum ne is mein stock, qeemat aur budget ka hisaab shamil kiya hai. App batati hai kitna samaan pehle se mojood hai, kitna mazeed khareedna hai aur kitna kharcha ayega. Python hisaab karta hai; AI us hisaab ko asaan alfaaz mein samjhati hai. Yeh final engineering approval nahin hai.”

## Before recording

- Close unrelated windows and notifications.
- Load the demo and verify the displayed totals.
- Test the live API before recording or use the offline mode honestly.
- Do not show API keys or private settings in the video.
- Keep all submission links viewable by judges.
- Add real names and real contributions; no placeholders in submitted slides.

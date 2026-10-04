# Start here — final hackathon upgrade

Your new project name is **ConcreteAI SitePlan**.

## 1. Run it first

1. Extract the ZIP.
2. Open the `concrete-mix-agent-main` folder in your terminal.
3. Run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

4. Click **Load demo project** in the sidebar.
5. You should see **150.0 cft**, **4.46 m³ including allowance**, **PKR 42,845 remaining purchases plus delivery**, and **PKR 7,155 budget remaining**. Rates are invented demonstration inputs.

## 2. Update your GitHub project

Keep a backup of the old project. Upload the extracted files into the root of your existing repository. Replace the old `app.py`, `mix_design_tool.py`, `requirements.txt` and `README.md`; add `purchase_planner.py`, `agent.py`, the documentation and tests. Do not upload only the ZIP. The `app.py` file should be directly in the configured application folder, not hidden inside an extra nested folder.

Commit the changes. Keep your existing repository connected to Streamlit if it is already deployed. Check that the app uses `app.py` and that its dependency installation succeeds. Use Python 3.12 when selecting the runtime. If your app does not update automatically, use its management controls to restart/redeploy it.

This ZIP has not been uploaded to your GitHub account or deployed for you.

## 3. Enable Claude if you have an API key

The calculator does not need a key. To demonstrate real live tool use, add these values in the app's Streamlit secrets settings:

```toml
ANTHROPIC_API_KEY = "YOUR_API_KEY"
ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
```

Use your real API key only in the private secrets settings, never in GitHub. Alternatively use the app's masked session key field. A ChatGPT subscription is not an Anthropic API key.

Open **AI assistant**, click **Run live agent**, and check that the result shows a live mode and actual tool calls. If it shows API unavailable, fix the connection or demonstrate the offline calculator honestly. Offline summary is not live AI.

## 4. Prepare the submission

The supplied guideline PDF asks for:

- App/deployment link.
- Code link.
- Presentation slides link with team members' information.
- PRD link covering finance, requirements, tools/technologies and scope.
- A 4–5 minute presentation video covering slides, app demo and team contributions.
- Team of 4–6 members including the leader.
- All links viewable by judges.

Use `PRD.md` as your PRD source and `DEMO_GUIDE.md` for presentation content. Add your actual team names, contributions and links; no identities or contributions have been invented. Slides and a video are not included in this code package.

Present this as an upgrade to your earlier work. The supplied guidelines do not clearly establish whether reused work is eligible.

## 5. What to say changed

“We extended our concrete mix prototype into a material purchase planner. It subtracts stock, calculates remaining purchase costs, checks a budget, and exports a purchase list. Python performs the arithmetic; optional Claude tool-use explains the confirmed results.”

Do not call it a certified design or promise savings without measurements. Do not claim the default prices are today's market prices.

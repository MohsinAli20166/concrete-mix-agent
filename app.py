import os, json
import streamlit as st
from mix_design_tool import calculate_mix_design, EXPOSURE_RULES, STRUCTURE_RULES, suggest_grade, M3_TO_CFT

BAG_CFT = 1.25   # site convention: 1 bag of 50 kg cement = 1.25 cft

st.set_page_config(page_title="ConcreteAI", page_icon="🏗️", layout="wide")
st.title("🏗️ ConcreteAI — Agentic ACI 211.1 Mix Design Assistant")
st.caption("PakAngel GenAI & Agentic AI Cohort C11 · Code basis: ACI 211.1 / ACI 318 / Pakistan Building Code 2021 · Units: psi, cft, L")

lang = st.sidebar.selectbox("🌐 Language / زبان", ["English", "Urdu (اردو)", "Roman Urdu"])

TOOL_SCHEMA = [{
    "name": "calculate_mix_design",
    "description": "Calculate ACI 211.1 concrete mix quantities per cubic meter.",
    "input_schema": {
        "type": "object",
        "properties": {
            "target_strength_psi": {"type": "integer", "description": "Target 28-day strength in psi"},
            "exposure": {"type": "string", "enum": ["mild", "moderate", "severe", "coastal"]},
        },
        "required": ["target_strength_psi", "exposure"],
    },
}]
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")

def agent_run_llm(text, lang):
    """Real agentic loop: Claude infers params, CALLS the tool, then explains in chosen language."""
    import anthropic
    instr = {"Urdu (اردو)": "\n(Respond fully in Urdu script.)",
             "Roman Urdu": "\n(Respond fully in Roman Urdu / Latin script.)"}.get(lang, "")
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    r1 = client.messages.create(model=MODEL, max_tokens=1024, tools=TOOL_SCHEMA,
                                messages=[{"role": "user", "content": text + instr}])
    for block in r1.content:
        if block.type == "tool_use":
            args = block.input
            result = calculate_mix_design(args.get("target_strength_psi", 3000),
                                          args.get("exposure", "mild"))
            r2 = client.messages.create(
                model=MODEL, max_tokens=1024, tools=TOOL_SCHEMA,
                messages=[
                    {"role": "user", "content": text + instr},
                    {"role": "assistant", "content": r1.content},
                    {"role": "user", "content": [{"type": "tool_result", "tool_use_id": block.id,
                                                  "content": json.dumps(result)}]},
                ])
            explanation = "".join(b.text for b in r2.content if b.type == "text")
            return args, result, explanation, "LLM agentic mode (Claude tool-call)"
    raise RuntimeError("LLM did not call the tool")

def _explain(result, lang):
    ratio = result["site_ratio_per_bag"]
    cement_cft = round(result["cement_bags_50kg"] * BAG_CFT, 1)
    if lang == "Urdu (اردو)":
        return (f"آپ کے {result['exposure']} ماحول کے لیے ایجنٹ نے {result['final_psi']} psi کنکریٹ منتخب کیا ہے۔ "
                f"پانی-سیمنٹ تناسب {result['wc_ratio']} ہے، جس سے فی مکعب میٹر {cement_cft} cft سیمنٹ، "
                f"{result['sand_cft_m3']} cft ریت اور {result['coarse_agg_cft_m3']} cft کرشری ملتی ہے۔ "
                f"سائٹ ریشو (فی بوری): {ratio}۔ یہ ACI 211.1 کے مطابق ابتدائی تخمینہ ہے؛ حتمی ڈیزائن کے لیے لیب ٹرائل ضروری ہے۔")
    if lang == "Roman Urdu":
        return (f"Aap ke {result['exposure']} exposure ke liye agent ne {result['final_psi']} psi concrete select kiya hai. "
                f"Paani-cement ratio {result['wc_ratio']} hai, jis se fi cubic meter {cement_cft} cft cement, "
                f"{result['sand_cft_m3']} cft ret aur {result['coarse_agg_cft_m3']} cft crush milti hai. "
                f"Site ratio (fi bori): {ratio}. Ye ACI 211.1 ke mutabiq initial estimate hai; final design ke liye lab trial zaroori hai.")
    return (f"For your {result['exposure']} exposure scenario, the agent selected {result['final_psi']} psi concrete. "
            f"The governing water-cement ratio is {result['wc_ratio']}, giving per cubic meter: {cement_cft} cft cement, "
            f"{result['sand_cft_m3']} cft sand and {result['coarse_agg_cft_m3']} cft coarse aggregate. "
            f"Site ratio per bag of cement: {ratio}. These are ACI 211.1 absolute-volume estimates for trial batches.")

def agent_run_fallback(text, lang):
    """Offline fallback: keyword inference + same deterministic tool."""
    t = text.lower()
    exposure, psi = "mild", 3000
    if any(w in t for w in ["sea", "coast", "chloride", "sulfate", "sulphate", "chemical", "sewage", "samandar"]):
        exposure, psi = "coastal", 4000
    elif any(w in t for w in ["freeze", "freezing", "cold", "mountain", "northern"]):
        exposure, psi = "severe", 3500
    elif any(w in t for w in ["rain", "wet", "underground", "foundation", "basement", "water tank"]):
        exposure, psi = "moderate", 3000
    for v in [2000, 2500, 3000, 3500, 4000, 4500, 5000]:
        if str(v) in t:
            psi = v
    args = {"target_strength_psi": psi, "exposure": exposure}
    result = calculate_mix_design(psi, exposure)
    return args, result, _explain(result, lang), "OFFLINE fallback mode (keyword agent + same tool)"

def show_result(args, result, explanation, mode, lang):
    st.success(f"🤖 Mode: {mode}\n\nAgent inferred → strength: **{args['target_strength_psi']} psi**, exposure: **{args['exposure']}** → called `calculate_mix_design()`")
    for w in result["warnings"]:
        st.error("⚠️ " + w)
    if result["warnings"] and lang == "Urdu (اردو)":
        st.warning("ضروری نوٹ: کوڈ (ACI 318 / PBC 2021) کے مطابق اس ماحول کے لیے کم از کم strength لازمی ہے، اس لیے ویلیوز خودکار طور پر ایڈجسٹ کی گئی ہیں۔")
    elif result["warnings"] and lang == "Roman Urdu":
        st.warning("Zaroori note: code (ACI 318 / PBC 2021) ke mutabiq is exposure ke liye minimum strength lazmi hai, is liye values khud-ba-khud adjust ki gayi hain.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cement / سیمنٹ", f"{round(result['cement_bags_50kg'] * BAG_CFT, 1)} cft")
    c2.metric("Sand / ریت", f"{result['sand_cft_m3']} cft")
    c3.metric("Coarse Agg / کرشری", f"{result['coarse_agg_cft_m3']} cft")
    c4.metric("Water / پانی", f"{result['water_kg_m3']} L")
    st.caption(f"Per 1 m³ → Cement {result['cement_kg_m3']} kg · Sand {result['sand_kg_m3']} kg · Crush {result['coarse_agg_kg_m3']} kg")
    st.info("🧱 **Site ratio (per 1 bag cement / فی بوری ریشو):** `" + result["site_ratio_per_bag"] + "`")
    st.info("**Agent explanation / وضاحت:**\n\n" + explanation)
    with st.expander("🔎 Full tool output (JSON)"):
        st.json(result)

with st.sidebar:
    st.header("🧮 Manual Calculator / دستی کیلکولیٹر")
    psi = st.number_input("Target strength (psi)", 1500, 8000, 3000, step=500)
    exp = st.selectbox("Exposure", list(EXPOSURE_RULES.keys()), key="sb_exp")
    struct_sel = st.selectbox("Structure type / ساخت کی قسم", [r[0] for r in STRUCTURE_RULES], key="sb_struct")
    if st.button("Calculate mix / مکس نکالیں", type="primary"):
        res = calculate_mix_design(psi, exp)
        sugg = suggest_grade(struct_sel, exp)
        st.info(f"💡 **Suggested grade / تجویز کردہ گریڈ:** {sugg['suggested_psi']} psi (≈{sugg['mpa_equiv']} MPa) "
                f"for {sugg['structure']} — {sugg['reason']}")
        show_result({"target_strength_psi": psi, "exposure": exp}, res,
                    _explain(res, lang), "Manual tool mode", lang)
    st.divider()
    st.caption("⚠️ Prototype for preliminary estimation & learning. Real projects require lab trial mixes and engineer sign-off.")

st.header("📐 Area-wise Quantity Calculator / رقبہ کے حساب سے مقدار")
a1, a2, a3, a4, a5 = st.columns(5)
with a1:
    length_ft = st.number_input("Length / لمبائی (ft)", 0.0, 1000.0, 20.0, 0.5)
with a2:
    width_ft = st.number_input("Width / چوڑائی (ft)", 0.0, 1000.0, 15.0, 0.5)
with a3:
    thick_ft = st.number_input("Thickness / موٹائی (ft)", 0.0, 10.0, 0.5, 0.25)
with a4:
    area_psi = st.number_input("Strength (psi)", 1500, 8000, 3000, step=500)
with a5:
    area_exp = st.selectbox("Exposure", list(EXPOSURE_RULES.keys()), key="area_exp")
if st.button("Calculate total quantities / کل مقدار نکالیں", type="primary"):
    vol_cft = length_ft * width_ft * thick_ft
    vol_m3 = vol_cft / M3_TO_CFT
    res = calculate_mix_design(area_psi, area_exp)
    tot_cement_cft = res["cement_kg_m3"] * vol_m3 / 50.0 * BAG_CFT
    tot_sand = res["sand_cft_m3"] * vol_m3
    tot_agg = res["coarse_agg_cft_m3"] * vol_m3
    tot_water = res["water_kg_m3"] * vol_m3
    st.success(f"📦 Concrete volume: **{round(vol_cft, 1)} cft = {round(vol_m3, 2)} m³**")
    for w in res["warnings"]:
        st.error("⚠️ " + w)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Cement / کل سیمنٹ", f"{round(tot_cement_cft, 1)} cft")
    m2.metric("Total Sand / کل ریت", f"{round(tot_sand, 1)} cft")
    m3.metric("Total Crush / کل کرشری", f"{round(tot_agg, 1)} cft")
    m4.metric("Total Water / کل پانی", f"{round(tot_water, 0)} L")
    st.caption(f"Mix used: {res['final_psi']} psi · {res['exposure']} exposure · ratio {res['site_ratio_per_bag']}")

st.header("💬 Agentic Chat / ایجنٹ چیٹ")
prompt = st.text_area("Describe your structure in plain English or Urdu-English mix:",
                      placeholder="e.g. I am building a boundary wall for a house near the sea in Karachi, what concrete should I use?",
                      height=100)
if st.button("Run Agent / ایجنٹ چلائیں", type="primary") and prompt.strip():
    with st.spinner("Agent is reading your scenario and deciding whether to call the tool..."):
        try:
            if os.environ.get("ANTHROPIC_API_KEY"):
                args, result, explanation, mode = agent_run_llm(prompt, lang)
            else:
                args, result, explanation, mode = agent_run_fallback(prompt, lang)
        except Exception as e:
            st.warning(f"LLM unavailable ({type(e).__name__}) — switching to offline fallback agent.")
            args, result, explanation, mode = agent_run_fallback(prompt, lang)
        sugg = suggest_grade(prompt, args["exposure"])
        st.info(f"💡 **Suggested grade / تجویز کردہ گریڈ:** {sugg['suggested_psi']} psi (≈{sugg['mpa_equiv']} MPa) "
                f"for {sugg['structure']} — {sugg['reason']}")
        show_result(args, result, explanation, mode, lang)

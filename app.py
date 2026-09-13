import os, json
import streamlit as st
from mix_design_tool import calculate_mix_design, EXPOSURE_RULES

st.set_page_config(page_title="ConcreteAI", page_icon="🏗️", layout="wide")
st.title("🏗️ ConcreteAI — Agentic ACI 211.1 Mix Design Assistant")
st.caption("PakAngel GenAI & Agentic AI Cohort C11 · Code basis: ACI 211.1 / ACI 318 / Pakistan Building Code 2021 · Units: psi, kg/m³")

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
    if lang == "Urdu (اردو)":
        return (f"آپ کے {result['exposure']} ماحول کے لیے ایجنٹ نے {result['final_psi']} psi کنکریٹ منتخب کیا ہے۔ "
                f"پانی-سیمنٹ تناسب {result['wc_ratio']} ہے، جس سے فی مکعب میٹر {result['cement_kg_m3']} کلو سیمنٹ "
                f"({result['cement_bags_50kg']} بورے)، {result['sand_kg_m3']} کلو ریت اور {result['coarse_agg_kg_m3']} کلو کرشری ملتی ہے۔ "
                f"یہ ACI 211.1 کے مطابق ابتدائی تخمینہ ہے؛ حتمی ڈیزائن کے لیے لیب ٹرائل ضروری ہے۔")
    if lang == "Roman Urdu":
        return (f"Aap ke {result['exposure']} exposure ke liye agent ne {result['final_psi']} psi concrete select kiya hai. "
                f"Paani-cement ratio {result['wc_ratio']} hai, jis se fi cubic meter {result['cement_kg_m3']} kg cement "
                f"({result['cement_bags_50kg']} bore), {result['sand_kg_m3']} kg ret aur {result['coarse_agg_kg_m3']} kg crush milti hai. "
                f"Ye ACI 211.1 ke mutabiq initial estimate hai; final design ke liye lab trial zaroori hai.")
    return (f"For your {result['exposure']} exposure scenario, the agent selected {result['final_psi']} psi concrete. "
            f"The governing water-cement ratio is {result['wc_ratio']}, giving {result['cement_kg_m3']} kg cement "
            f"({result['cement_bags_50kg']} bags of 50 kg), {result['sand_kg_m3']} kg sand and "
            f"{result['coarse_agg_kg_m3']} kg coarse aggregate per cubic meter. "
            f"These are ACI 211.1 absolute-volume estimates for trial batches.")

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
    c1.metric("Cement / سیمنٹ", f"{result['cement_kg_m3']} kg/m³")
    c2.metric("Sand / ریت", f"{result['sand_kg_m3']} kg/m³")
    c3.metric("Coarse Agg / کرشری", f"{result['coarse_agg_kg_m3']} kg/m³")
    c4.metric("Water / پانی", f"{result['water_kg_m3']} L/m³")
    st.info("**Agent explanation / وضاحت:**\n\n" + explanation)
    with st.expander("🔎 Full tool output (JSON)"):
        st.json(result)

with st.sidebar:
    st.header("🧮 Manual Calculator / دستی کیلکولیٹر")
    psi = st.number_input("Target strength (psi)", 1500, 8000, 3000, step=500)
    exp = st.selectbox("Exposure", list(EXPOSURE_RULES.keys()))
    if st.button("Calculate mix / مکس نکالیں", type="primary"):
        show_result({"target_strength_psi": psi, "exposure": exp},
                    calculate_mix_design(psi, exp),
                    _explain(calculate_mix_design(psi, exp), lang),
                    "Manual tool mode", lang)
    st.divider()
    st.caption("⚠️ Prototype for preliminary estimation & learning. Real projects require lab trial mixes and engineer sign-off.")

st.header("💬 Agentic Chat / ایجنٹ چیٹ")
prompt = st.text_area("Describe your structure in plain English or Urdu-English mix:",
                      placeholder="e.g. I am building a boundary wall for a house near the sea in Karachi, what concrete should I use?",
                      height=100)
if st.button("Run Agent / ایجنٹ چلائیں", type="primary") and prompt.strip():
    with st.spinner("Agent is reading your scenario and deciding whether to call the tool..."):
        try:
            if os.environ.get("ANTHROPIC_API_KEY"):
                show_result(*agent_run_llm(prompt, lang), lang)
            else:
                show_result(*agent_run_fallback(prompt, lang), lang)
        except Exception as e:
            st.warning(f"LLM unavailable ({type(e).__name__}) — switching to offline fallback agent.")
            show_result(*agent_run_fallback(prompt, lang), lang)

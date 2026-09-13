import os, json
import streamlit as st
from mix_design_tool import calculate_mix_design, EXPOSURE_RULES

st.set_page_config(page_title="ConcreteAI", page_icon="🏗️", layout="wide")
st.title("🏗️ ConcreteAI — Agentic ACI 211.1 Mix Design Assistant")
st.caption("PakAngel GenAI & Agentic AI Cohort C11 · Code basis: ACI 211.1 / ACI 318 / Pakistan Building Code 2021 · Units: psi, kg/m³")

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

def agent_run_llm(text):
    """Real agentic loop: Claude infers params, CALLS the tool, then explains."""
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    r1 = client.messages.create(model=MODEL, max_tokens=1024, tools=TOOL_SCHEMA,
                                messages=[{"role": "user", "content": text}])
    for block in r1.content:
        if block.type == "tool_use":
            args = block.input
            result = calculate_mix_design(args.get("target_strength_psi", 3000),
                                          args.get("exposure", "mild"))
            r2 = client.messages.create(
                model=MODEL, max_tokens=1024, tools=TOOL_SCHEMA,
                messages=[
                    {"role": "user", "content": text},
                    {"role": "assistant", "content": r1.content},
                    {"role": "user", "content": [{"type": "tool_result", "tool_use_id": block.id,
                                                  "content": json.dumps(result)}]},
                ])
            explanation = "".join(b.text for b in r2.content if b.type == "text")
            return args, result, explanation, "LLM agentic mode (Claude tool-call)"
    raise RuntimeError("LLM did not call the tool")

def agent_run_fallback(text):
    """Offline fallback: keyword inference + same deterministic tool."""
    t = text.lower()
    exposure, psi = "mild", 3000
    if any(w in t for w in ["sea", "coast", "chloride", "sulfate", "sulphate", "chemical", "sewage"]):
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
    explanation = (f"For your {result['exposure']} exposure scenario, the agent selected {result['final_psi']} psi concrete. "
                   f"The governing water-cement ratio is {result['wc_ratio']}, giving {result['cement_kg_m3']} kg cement "
                   f"({result['cement_bags_50kg']} bags of 50 kg), {result['sand_kg_m3']} kg sand and "
                   f"{result['coarse_agg_kg_m3']} kg coarse aggregate per cubic meter. "
                   f"These are ACI 211.1 absolute-volume estimates for trial batches.")
    return args, result, explanation, "OFFLINE fallback mode (keyword agent + same tool)"

def show_result(args, result, explanation, mode):
    st.success(f"🤖 Mode: {mode}\n\nAgent inferred → strength: **{args['target_strength_psi']} psi**, exposure: **{args['exposure']}** → called `calculate_mix_design()`")
    for w in result["warnings"]:
        st.error("⚠️ " + w)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cement", f"{result['cement_kg_m3']} kg/m³")
    c2.metric("Sand", f"{result['sand_kg_m3']} kg/m³")
    c3.metric("Coarse Agg", f"{result['coarse_agg_kg_m3']} kg/m³")
    c4.metric("Water", f"{result['water_kg_m3']} L/m³")
    st.info("**Agent explanation:**\n\n" + explanation)
    with st.expander("🔎 Full tool output (JSON)"):
        st.json(result)

with st.sidebar:
    st.header("🧮 Manual Calculator (deterministic tool)")
    psi = st.number_input("Target strength (psi)", 1500, 8000, 3000, step=500)
    exp = st.selectbox("Exposure", list(EXPOSURE_RULES.keys()))
    if st.button("Calculate mix", type="primary"):
        show_result({"target_strength_psi": psi, "exposure": exp},
                    calculate_mix_design(psi, exp),
                    "Deterministic ACI 211.1 absolute-volume calculation (no AI involved).",
                    "Manual tool mode")
    st.divider()
    st.caption("⚠️ Prototype for preliminary estimation & learning. Real projects require lab trial mixes and engineer sign-off.")

st.header("💬 Agentic Chat")
prompt = st.text_area("Describe your structure in plain English (Urdu-English mix is fine):",
                      placeholder="e.g. I am building a boundary wall for a house near the sea in Karachi, what concrete should I use?",
                      height=100)
if st.button("Run Agent", type="primary") and prompt.strip():
    with st.spinner("Agent is reading your scenario and deciding whether to call the tool..."):
        try:
            if os.environ.get("ANTHROPIC_API_KEY"):
                show_result(*agent_run_llm(prompt))
            else:
                show_result(*agent_run_fallback(prompt))
        except Exception as e:
            st.warning(f"LLM unavailable ({type(e).__name__}) — switching to offline fallback agent.")
            show_result(*agent_run_fallback(prompt))

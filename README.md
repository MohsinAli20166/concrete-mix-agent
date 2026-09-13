# 🏗️ ConcreteAI — Agentic AI Assistant for ACI-Based Concrete Mix Design

**PakAngel GenAI & Agentic AI Cohort C11 Hackathon Project**

ConcreteAI is an agentic AI assistant that automates preliminary concrete mix design calculations per **ACI 211.1 / ACI 318** (as referenced by the **Pakistan Building Code 2021**).

Instead of hallucinating engineering data, the LLM agent reads a plain-English site scenario, infers the required strength (psi) and exposure class, and **calls a deterministic calculation tool**. It then generates a clear, code-compliant explanation in **English, Urdu (اردو), or Roman Urdu**.

## 🚀 Key Features
*   **Agentic Chat:** Real tool-calling via LLM (Anthropic Claude) + offline keyword fallback agent.
*   **Deterministic Tool:** 100% accurate ACI 211.1 absolute-volume calculations (no AI guessing).
*   **Durability Overrides:** Automatic warnings when ACI 318 exposure rules override user-requested strength.
*   **Multilingual:** Explanations available in English, Urdu (اردو), and Roman Urdu so local contractors can use it directly.
*   **Manual Calculator:** Sidebar tool for quick, deterministic lookups.

## ⚙️ Tech Stack
*   Python
*   Streamlit (UI & Deployment)
*   Anthropic Claude (Agentic Tool-Calling)
*   ACI 211.1 Mathematical Logic

## 🖥️ Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py

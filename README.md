# 🏗️ ConcreteAI — Agentic AI Assistant for ACI-Based Concrete Mix Design

**PakAngel GenAI & Agentic AI Cohort C11 Hackathon Project**

ConcreteAI is an agentic AI assistant that automates preliminary concrete mix design per ACI 211.1 / ACI 318 (Pakistan Building Code 2021). The LLM agent reads a plain-English site scenario, infers strength (psi) and exposure class, calls a deterministic calculation tool, and explains the compliant mix in English, Urdu (اردو), or Roman Urdu.

## 🚀 Key Features
- Agentic chat: real LLM tool-calling (Anthropic Claude) + offline keyword fallback
- Deterministic ACI 211.1 absolute-volume calculator (no AI-guessed numbers)
- Durability override warnings (ACI 318 / PBC 2021)
- Multilingual explanations: English, Urdu, Roman Urdu for local contractors
- Manual calculator sidebar

## ⚙️ Tech Stack
Python · Streamlit · Anthropic Claude · ACI 211.1 calculation module

## 🖥️ Run Locally
Install: pip install -r requirements.txt  —  then run: streamlit run app.py

## ⚠️ Limitations
- Prototype for preliminary estimation and trial batches only
- Fixed material assumptions (20 mm aggregate, 75–100 mm slump, FM 2.8 sand)
- Not a final design: lab trials and engineer sign-off required

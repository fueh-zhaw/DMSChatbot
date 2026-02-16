# Gradio-in-Streamlit Demo (Variante A)

Diese Demo startet lokal einen **Gradio-Server** und bettet ihn in eine **Streamlit-App** per iframe ein.
Die Stimmungsanalyse ist **regelbasiert** (DE/EN) und kommt ohne ML-Modelle aus.

## Voraussetzungen
- Python 3.9+ empfohlen
- Ports für localhost verfügbar (Standard: 7860)

## Installation
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

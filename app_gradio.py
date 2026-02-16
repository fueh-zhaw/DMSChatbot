# app_gradio.py
import gradio as gr
from core import analyze_text

APP_TITLE = "Stimmungs-Demo (regelbasiert)"
APP_DESC = "Gib einen kurzen Text ein. Die Regelheuristik schätzt die Stimmung (DE/EN)."

def predict_interface(text: str) -> str:
    if not text or not text.strip():
        return "Bitte Text eingeben."
    res = analyze_text(text)
    md = f"### Ergebnis: {res['emoji']} **{res['label'].capitalize()}** (Konfidenz: {res['confidence']})\n"
    md += f"- **Positiv-Treffer:** {res['details']['pos_hits']}\n"
    md += f"- **Negativ-Treffer:** {res['details']['neg_hits']}\n"
    md += f"- **Begründung:** {res['details']['rationale']}\n"
    return md

def build_app() -> gr.Blocks:
    with gr.Blocks(title=APP_TITLE, theme=gr.themes.Soft()) as demo:
        gr.Markdown(f"# {APP_TITLE}\n{APP_DESC}")
        with gr.Row():
            inp = gr.Textbox(lines=4, label="Text")
        btn = gr.Button("Analysieren")
        out = gr.Markdown(label="Analyse")
        btn.click(fn=predict_interface, inputs=inp, outputs=out)
    return demo

def main(host: str = "0.0.0.0", port: int = 7860):
    app = build_app()
    app.queue()  # ermöglicht parallele Requests
    app.launch(server_name=host, server_port=port, share=False, show_error=True)

if __name__ == "__main__":
    main()

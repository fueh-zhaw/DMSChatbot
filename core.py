# core.py
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Dict

@dataclass
class SentimentResult:
    label: str        # "positive" | "negative" | "neutral"
    emoji: str        # 😊 😢 😐
    confidence: float # 0.0 .. 1.0
    rationale: str    # kurze Begründung

_POSITIVE_TERMS = {
    "de": ["gut", "toll", "super", "freu", "glück", "zufried", "danke", "top", "stark", "genial", "cool", "nice"],
    "en": ["good", "great", "awesome", "happy", "joy", "love", "nice", "excellent", "wonderful", "amazing", "cool"],
}
_NEGATIVE_TERMS = {
    "de": ["schlecht", "traurig", "doof", "ärger", "wütend", "katastroph", "mies", "enttäusch", "furchtbar", "mist"],
    "en": ["bad", "sad", "angry", "terrible", "awful", "hate", "horrible", "disappoint", "worse", "worst"],
}
_NEGATION_TERMS = ["nicht", "kein", "never", "no", "none", "ohne"]

# einfache Normalisierung
def _normalize(text: str) -> str:
    text = text.strip().lower()
    # Umlaute vereinheitlichen (nur minimal)
    text = text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return text

def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-ZäöüÄÖÜß\-]+", text.lower())

def analyze_text(text: str) -> Dict[str, object]:
    """
    Regelbasierte Stimmung:
    - zählt Treffer aus Positiv-/Negativlexika (DE + EN)
    - berücksichtigt simple Negation in Fenstergröße 3 Tokens
    - leitet Label + Emoji + pseudo-Confidence ab
    """
    tnorm = _normalize(text)
    tokens = _tokenize(tnorm)

    pos_hits = 0
    neg_hits = 0
    rationales = []

    def is_negated(idx: int) -> bool:
        # sehr simple Heuristik: Negation in den letzten 3 Tokens
        start = max(0, idx - 3)
        window = tokens[start:idx]
        return any(ng in window for ng in _NEGATION_TERMS)

    # Trefferzählung mit Negations-Umkehr
    for i, tok in enumerate(tokens):
        # Deutsche/Englische Stämme via startswith-Heuristik erfassen (z. B. "glücklich" → "glueck")
        if any(tok.startswith(term) for term in _POSITIVE_TERMS["de"] + _POSITIVE_TERMS["en"]):
            if is_negated(i):
                neg_hits += 1
                rationales.append(f"Negiertes positiv: „{tok}“ → negativ gewertet")
            else:
                pos_hits += 1
                rationales.append(f"Positiv: „{tok}“")
        elif any(tok.startswith(term) for term in _NEGATIVE_TERMS["de"] + _NEGATIVE_TERMS["en"]):
            if is_negated(i):
                pos_hits += 1
                rationales.append(f"Negiertes negativ: „{tok}“ → positiv gewertet")
            else:
                neg_hits += 1
                rationales.append(f"Negativ: „{tok}“")

    # Label bestimmen
    if pos_hits > neg_hits:
        label, emoji = "positive", "😊"
    elif neg_hits > pos_hits:
        label, emoji = "negative", "😢"
    else:
        label, emoji = "neutral", "😐"

    # Pseudo-Confidence: saturierte Sigmoid auf (pos-neg)
    margin = pos_hits - neg_hits
    # einfache S-Kurve (keine externen Libs)
    confidence = 1.0 / (1.0 + pow(2.71828, -1.2 * margin))
    # neutral etwas in die Mitte ziehen
    if label == "neutral":
        confidence = 0.55 if (pos_hits + neg_hits) > 0 else 0.5

    rationale = " | ".join(rationales) if rationales else "Keine eindeutigen Stimmungsbegriffe erkannt."
    return {
        "label": label,
        "emoji": emoji,
        "confidence": round(float(confidence), 2),
        "details": {
            "pos_hits": pos_hits,
            "neg_hits": neg_hits,
            "rationale": rationale,
        },
    }

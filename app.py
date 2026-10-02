"""
CodeAlpha AI Internship - Task 1: Language Translation Tool

Streamlit UI. Tries Google Translate first (short timeout so it never hangs),
then falls back to Argos Translate (open-source, runs locally).
Optional: copy button on the output box and text-to-speech (gTTS).
"""

import io

import requests
import streamlit as st

st.set_page_config(page_title="Language Translation Tool", page_icon="🌐")
st.title("🌐 Language Translation Tool")

LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Arabic": "ar",
    "Chinese": "zh",
    "Japanese": "ja",
    "Russian": "ru",
    "Portuguese": "pt",
    "Italian": "it",
}


def google_translate(text, src, tgt):
    """Free Google Translate endpoint. Raises on any failure (8 s timeout)."""
    r = requests.get(
        "https://translate.googleapis.com/translate_a/single",
        params={"client": "gtx", "sl": src, "tl": tgt, "dt": "t", "q": text},
        timeout=8,
    )
    r.raise_for_status()
    data = r.json()
    return "".join(part[0] for part in data[0] if part[0])


# ---------- Offline fallback (Argos Translate) ----------
def argos_translate(text, src, tgt):
    import argostranslate.package
    import argostranslate.translate

    def get_translation(a, b):
        langs = argostranslate.translate.get_installed_languages()
        la = next((l for l in langs if l.code == a), None)
        lb = next((l for l in langs if l.code == b), None)
        return la.get_translation(lb) if la and lb else None

    if src == "auto":
        raise RuntimeError("Auto-detect needs Google; please choose a source language.")

    if not get_translation(src, tgt):
        steps = []
        if src != "en":
            steps.append((src, "en"))
        if tgt != "en":
            steps.append(("en", tgt))
        argostranslate.package.update_package_index()
        available = argostranslate.package.get_available_packages()
        for a, b in steps:
            if not get_translation(a, b):
                pkg = next(
                    (p for p in available if p.from_code == a and p.to_code == b), None
                )
                if pkg is None:
                    raise RuntimeError(f"No offline model for {a} -> {b}")
                argostranslate.package.install_from_path(pkg.download())
    return get_translation(src, tgt).translate(text)


def translate(text, src, tgt):
    try:
        return google_translate(text, src, tgt), "Google Translate"
    except Exception as google_err:
        try:
            return argos_translate(text, src, tgt), "Argos Translate (offline)"
        except Exception as argos_err:
            raise RuntimeError(
                f"Google failed ({type(google_err).__name__}) and offline fallback "
                f"failed ({type(argos_err).__name__}: {argos_err})"
            )


names = list(LANGUAGES.keys())
col1, col2 = st.columns(2)
with col1:
    source_name = st.selectbox("From", ["Auto-detect"] + names, index=1)
with col2:
    target_name = st.selectbox("To", names, index=names.index("Hindi"))

text = st.text_area("Enter text", height=150, placeholder="Type or paste text here...")

if st.button("Translate", type="primary"):
    src = "auto" if source_name == "Auto-detect" else LANGUAGES[source_name]
    tgt = LANGUAGES[target_name]
    if not text.strip():
        st.warning("Please enter some text to translate.")
    elif src == tgt:
        st.warning("Source and target languages are the same.")
    else:
        try:
            with st.spinner("Translating..."):
                result, engine = translate(text, src, tgt)
            st.session_state["result"] = result
            st.session_state["engine"] = engine
            st.session_state["target"] = tgt
        except Exception as e:
            st.error(f"Translation failed: {e}")

if "result" in st.session_state:
    st.subheader("Translation")
    # st.code shows a built-in copy button in the top-right corner
    st.code(st.session_state["result"], language=None, wrap_lines=True)
    st.caption(f"Translated with {st.session_state['engine']}")

    if st.button("🔊 Listen"):
        try:
            from gtts import gTTS

            audio = io.BytesIO()
            gTTS(
                st.session_state["result"], lang=st.session_state["target"]
            ).write_to_fp(audio)
            st.audio(audio.getvalue(), format="audio/mp3")
        except Exception as e:
            st.error(f"Text-to-speech unavailable (needs internet): {e}")

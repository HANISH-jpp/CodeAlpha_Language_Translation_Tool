# CodeAlpha_Language_Translation_Tool

CodeAlpha AI Internship – Task 1.

A Streamlit web app where you type text, choose source and target languages, and get the translation.

## Features
- Source language (or auto-detect) and target language dropdowns
- Translation via Google Translate (`deep-translator`, no API key required)
- Copy button on the output box
- Text-to-speech playback (`gTTS`)

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```
(Needs an internet connection.)

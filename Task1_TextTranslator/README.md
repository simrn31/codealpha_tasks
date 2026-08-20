# Text Translator (Python / Tkinter)

A desktop translator app built with Python's built-in Tkinter GUI toolkit,
made as an internship task. Type text, choose a source and target language,
translate it, then copy the result or have it read aloud.


![English to Punjabi Translation](<en to pu.png>)
![English to Italian Translation](<en to it.png>)

## Features

- Text input box with a live character counter (500-character limit, turns
  red near the limit) and dropdowns for source/target language (20 languages)
- "Auto Detect" source language option
- Swap button to flip source ⇄ target, carrying the translated text back
  into the input box
- Calls the free [MyMemory Translation API](https://mymemory.translated.net/doc/spec.php) (no API key required)
- Runs the API call on a background thread, so the window never freezes
- Copy-to-clipboard button
- Text-to-speech ("Listen") button using [gTTS](https://gtts.readthedocs.io/)
  (Google Text-to-Speech) — chosen over Windows' built-in SAPI5 voices
  because it supports far more languages, including Hindi and Punjabi (see
  "Challenges" below for why)

## Setup

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run it
python translator.py
```

On Linux, if Tkinter isn't already installed:
```bash
sudo apt install python3-tk
```

**Note:** don't create the project inside a OneDrive-synced folder if
possible (see Challenges below) — a plain local folder avoids a permission
error when creating the virtual environment.

## Project structure

```
translator-app/
├── translator.py       # the whole app
├── requirements.txt
└── README.md
```

## How it works

- `LANGUAGES` maps human-readable names ("Hindi") to MyMemory's API codes
  ("hi"). `SPEECH_LANGUAGE_OVERRIDES` maps the handful of codes that differ
  between MyMemory and gTTS (currently just Chinese: `zh` → `zh-CN`).
- `translate_text()` sends a GET request to MyMemory with the text and
  `source|target` language pair, and returns `responseData.translatedText`
  from the JSON reply.
- `speak_text()` generates an MP3 with gTTS, saves it to a temporary file,
  plays it with `playsound`, then deletes it.
- `TranslatorApp` wires both functions up to the UI. Both the translate and
  speak calls run on a `threading.Thread` and post results back to the main
  thread with `root.after(...)`, which is the standard, safe way to update
  Tkinter widgets from a background thread.

## Challenges solved while building this

A few real debugging problems came up building this, worth documenting since
they're common Windows/Python gotchas:

- **`venv` creation failing with Permission denied`** — happened because the
  project folder was inside OneDrive, which locks files while syncing them.
  Fixed by moving the project to a plain local folder outside OneDrive.
- **`python`/`python3` not found despite Python being installed** — caused
  by Windows' "App execution alias" intercepting the command and redirecting
  to the Microsoft Store. Fixed by disabling the alias in Settings → Apps →
  Advanced app settings, and reinstalling with "Add to PATH" checked.
- **Text-to-speech producing no sound when called from a background
  thread** — `pyttsx3` uses SAPI5 via COM on Windows, and COM needs each
  thread to initialize its own COM context. Fixed initially with
  `pythoncom.CoInitialize()` inside the thread.
- **Text-to-speech only working for English/European languages** —
  Windows only ships SAPI5 voices for a handful of languages by default;
  Hindi and Punjabi voices aren't installed on most systems (and Punjabi
  often isn't available at all). Solved by switching from `pyttsx3`
  (offline, Windows-voice-dependent) to `gTTS` (online, much broader
  language coverage).

## Swapping in Google Translate or Microsoft Translator

MyMemory is free and key-free, which makes it a good default, but it's rate
limited (~500 characters per request for anonymous use). To use Google Cloud
Translation API or Microsoft Translator instead, replace the body of
`translate_text()` with a call to their REST endpoint and your API key —
the rest of the app (UI, threading, copy, speech) doesn't need to change.

Keep API keys out of source control: load them from an environment variable
(`os.environ.get("TRANSLATE_API_KEY")`) rather than hardcoding them, and add
a `.env` file (excluded via `.gitignore`) if you use one locally.

## Ideas for extending it further

- Translation history (save recent translations to a local file)
- Dark/light theme toggle
- A settings panel to remember the user's last-used language pair
- Adjustable speech rate/voice pitch for the Listen button

## License

MIT — free to reuse for learning.

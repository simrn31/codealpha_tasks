"""
Text Translator — Tkinter desktop app

Lets the user type text, pick a source and target language, and get a
translation using the free MyMemory Translation API (no API key needed).
Includes copy-to-clipboard and online text-to-speech (gTTS), which covers
far more languages than Windows' built-in SAPI5 voices.

Run:
    pip install -r requirements.txt
    python translator.py
"""

import os
import tempfile
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import requests
import pyperclip
from gtts import gTTS
from playsound import playsound

# ---------------------------------------------------------------
# Language list: display name -> API language code
#
# Note: gTTS and MyMemory mostly share codes, but a couple differ
# (e.g. Chinese). SPEECH_LANGUAGES overrides those specific cases;
# any language not listed there uses its MyMemory code for speech too.
# ---------------------------------------------------------------
LANGUAGES = {
    "Auto Detect": "autodetect",
    "English": "en",
    "Hindi": "hi",
    "Punjabi": "pa",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese (Simplified)": "zh",
    "Arabic": "ar",
    "Bengali": "bn",
    "Urdu": "ur",
    "Turkish": "tr",
    "Dutch": "nl",
    "Vietnamese": "vi",
    "Thai": "th",
    "Indonesian": "id",
}

# gTTS language codes that differ from the MyMemory codes above.
SPEECH_LANGUAGE_OVERRIDES = {
    "zh": "zh-CN",
}

# Target-language dropdown shouldn't offer "Auto Detect" — you can't
# translate *into* an unknown language.
TARGET_LANGUAGES = {name: code for name,
                    code in LANGUAGES.items() if name != "Auto Detect"}

MYMEMORY_URL = "https://api.mymemory.translated.net/get"
MAX_CHARS = 500


def translate_text(text: str, source_code: str, target_code: str) -> str:
    """Call the MyMemory API and return the translated text.

    Raises a RuntimeError with a human-readable message on failure.
    """
    params = {"q": text, "langpair": f"{source_code}|{target_code}"}

    try:
        response = requests.get(MYMEMORY_URL, params=params, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Network error: {exc}") from exc

    data = response.json()

    response_data = data.get("responseData") or {}
    translated = response_data.get("translatedText")

    if not translated:
        raise RuntimeError(
            "The translation service returned an unexpected response.")

    if data.get("responseStatus") not in (200, "200"):
        raise RuntimeError(
            data.get("responseDetails", "Translation service error."))

    return translated


def speak_text(text: str, language_code: str) -> None:
    """Synthesize and play speech for the given text using gTTS.

    Raises a RuntimeError with a human-readable message on failure.
    """
    speech_code = SPEECH_LANGUAGE_OVERRIDES.get(language_code, language_code)

    try:
        tts = gTTS(text=text, lang=speech_code)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tts.save(f.name)
            path = f.name
        playsound(path)
    except Exception as exc:  # gTTS/playsound raise several different types
        raise RuntimeError(f"Speech error: {exc}") from exc
    finally:
        try:
            if "path" in locals() and os.path.exists(path):
                os.remove(path)
        except OSError:
            pass  # best-effort cleanup; not worth failing the app over


class TranslatorApp:
    """The Tkinter GUI: wires the widgets to translate_text() and speak_text()."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Text Translator")
        self.root.geometry("560x520")
        self.root.minsize(480, 460)

        self.last_translation = ""

        self._build_ui()

    # ---------------------------------------------------------------
    # UI construction
    # ---------------------------------------------------------------
    def _build_ui(self):
        padding = {"padx": 12, "pady": 6}

        # --- language selectors row ---
        lang_frame = tk.Frame(self.root)
        lang_frame.pack(fill="x", **padding)

        tk.Label(lang_frame, text="From:").grid(row=0, column=0, sticky="w")
        self.source_lang = ttk.Combobox(
            lang_frame, values=list(LANGUAGES.keys()), state="readonly", width=20
        )
        self.source_lang.set("English")
        self.source_lang.grid(row=0, column=1, padx=(4, 20))

        swap_btn = tk.Button(lang_frame, text="⇄", width=3,
                             command=self.on_swap_click)
        swap_btn.grid(row=0, column=2, padx=(0, 20))

        tk.Label(lang_frame, text="To:").grid(row=0, column=3, sticky="w")
        self.target_lang = ttk.Combobox(
            lang_frame, values=list(TARGET_LANGUAGES.keys()), state="readonly", width=20
        )
        self.target_lang.set("Hindi")
        self.target_lang.grid(row=0, column=4, padx=(4, 0))

        # --- input box ---
        tk.Label(self.root, text="Enter text:").pack(anchor="w", **padding)
        self.input_text = tk.Text(self.root, height=6, wrap="word")
        self.input_text.pack(fill="x", padx=12)
        self.input_text.bind("<KeyRelease>", self.on_input_changed)

        self.char_count_label = tk.Label(
            self.root, text=f"0 / {MAX_CHARS}", fg="#6b7a80")
        self.char_count_label.pack(anchor="e", padx=12)

        # --- translate button + status ---
        action_frame = tk.Frame(self.root)
        action_frame.pack(fill="x", **padding)

        self.translate_btn = tk.Button(
            action_frame, text="Translate", command=self.on_translate_click, width=14
        )
        self.translate_btn.pack(side="left")

        self.status_label = tk.Label(action_frame, text="", fg="#2e5c8a")
        self.status_label.pack(side="left", padx=12)

        # --- output box ---
        tk.Label(self.root, text="Translation:").pack(anchor="w", **padding)
        self.output_text = tk.Text(
            self.root, height=6, wrap="word", state="disabled")
        self.output_text.pack(fill="x", padx=12)

        # --- copy / listen buttons ---
        output_actions = tk.Frame(self.root)
        output_actions.pack(fill="x", **padding)

        self.copy_btn = tk.Button(
            output_actions, text="Copy", command=self.on_copy_click, state="disabled"
        )
        self.copy_btn.pack(side="left")

        self.speak_btn = tk.Button(
            output_actions, text="Listen", command=self.on_speak_click, state="disabled"
        )
        self.speak_btn.pack(side="left", padx=8)

    # ---------------------------------------------------------------
    # Event handlers
    # ---------------------------------------------------------------
    def on_input_changed(self, _event=None):
        length = len(self.input_text.get("1.0", tk.END).rstrip("\n"))
        self.char_count_label.configure(
            text=f"{length} / {MAX_CHARS}",
            fg="#b23a2e" if length > MAX_CHARS else "#6b7a80",
        )

    def on_swap_click(self):
        src, tgt = self.source_lang.get(), self.target_lang.get()

        # "Auto Detect" only makes sense as a source, never as a target,
        # so don't let a swap put it into the target dropdown.
        if src == "Auto Detect":
            return

        self.source_lang.set(tgt)
        self.target_lang.set(src)

        # If there's already a translation, move it into the input box
        # so it can be sent back the other way.
        if self.last_translation:
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", self.last_translation)
            self.on_input_changed()

    def on_translate_click(self):
        text = self.input_text.get("1.0", tk.END).strip()
        source_name = self.source_lang.get()
        target_name = self.target_lang.get()

        if not text:
            messagebox.showwarning(
                "Nothing to translate", "Type some text first.")
            return
        if len(text) > MAX_CHARS:
            messagebox.showwarning(
                "Text too long",
                f"Please shorten your text to {MAX_CHARS} characters or fewer "
                "(the free translation API limits request size).",
            )
            return
        if source_name == target_name:
            messagebox.showwarning(
                "Same language", "Source and target languages are the same."
            )
            return

        source_code = LANGUAGES[source_name]
        target_code = LANGUAGES[target_name]

        self._set_translate_loading(True)

        # Run the network call on a background thread so the window
        # doesn't freeze while waiting for a response.
        thread = threading.Thread(
            target=self._translate_worker,
            args=(text, source_code, target_code),
            daemon=True,
        )
        thread.start()

    def _translate_worker(self, text, source_code, target_code):
        try:
            translated = translate_text(text, source_code, target_code)
            self.root.after(0, self._on_translate_success, translated)
        except RuntimeError as exc:
            self.root.after(0, self._on_translate_error, str(exc))

    def _on_translate_success(self, translated: str):
        self.last_translation = translated
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", translated)
        self.output_text.configure(state="disabled")

        self.copy_btn.configure(state="normal")
        self.speak_btn.configure(state="normal")
        self.status_label.configure(text="Done.", fg="#2e5c8a")
        self._set_translate_loading(False)

    def _on_translate_error(self, message: str):
        self.status_label.configure(text=message, fg="#b23a2e")
        self._set_translate_loading(False)

    def _set_translate_loading(self, is_loading: bool):
        self.translate_btn.configure(
            state="disabled" if is_loading else "normal",
            text="Translating…" if is_loading else "Translate",
        )
        if is_loading:
            self.status_label.configure(text="", fg="#2e5c8a")

    def on_copy_click(self):
        if not self.last_translation:
            return
        pyperclip.copy(self.last_translation)
        original = self.copy_btn["text"]
        self.copy_btn.configure(text="Copied")
        self.root.after(1200, lambda: self.copy_btn.configure(text=original))

    def on_speak_click(self):
        if not self.last_translation:
            return

        target_code = LANGUAGES[self.target_lang.get()]
        self._set_speak_loading(True)

        thread = threading.Thread(
            target=self._speak_worker, args=(
                self.last_translation, target_code), daemon=True
        )
        thread.start()

    def _speak_worker(self, text, language_code):
        try:
            speak_text(text, language_code)
            self.root.after(0, self._set_speak_loading, False)
        except RuntimeError as exc:
            self.root.after(0, self._on_speak_error, str(exc))

    def _on_speak_error(self, message: str):
        self.status_label.configure(text=message, fg="#b23a2e")
        self._set_speak_loading(False)

    def _set_speak_loading(self, is_loading: bool):
        self.speak_btn.configure(
            state="disabled" if is_loading else "normal",
            text="Playing…" if is_loading else "Listen",
        )


def main():
    root = tk.Tk()
    TranslatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

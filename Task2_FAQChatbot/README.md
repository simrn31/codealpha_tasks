# FAQ Chatbot (AI Internship - Task 2)

A chatbot that answers Frequently Asked Questions by matching a user's
question to the closest FAQ using **TF-IDF + cosine similarity**, with
a simple web-based chat UI.

## How it fulfills the task requirements

| Requirement | Where it's done |
|---|---|
| Collect FAQs (Q&A pairs) | `faqs.json` — 12 sample FAQs (edit freely, or swap in your own domain) |
| Preprocess the text using NLP libraries (NLTK) | `chatbot.py -> _preprocess()` — NLTK `word_tokenize`, stopword removal (`nltk.corpus.stopwords`), and lemmatization (`WordNetLemmatizer`) |
| Match user questions using cosine similarity | `chatbot.py -> get_response()` — TF-IDF vectorization + `cosine_similarity` |
| Display the best matching answer | Returned via `/api/chat` and shown in the chat UI |
| Optional: simple chat UI | `templates/index.html` — a clean chat-bubble interface |

## Project structure
```
faq_chatbot/
├── faqs.json          # FAQ dataset (question/answer pairs)
├── chatbot.py          # Core matching engine (preprocessing + TF-IDF + cosine similarity)
├── app.py              # Flask server (API + serves the UI)
├── templates/
│   └── index.html      # Chat interface
├── requirements.txt
└── README.md
```

## Setup & run

```bash
pip install -r requirements.txt
python app.py
```

The first time you run it, `chatbot.py` automatically downloads the
NLTK data it needs (`punkt`, `stopwords`, `wordnet`) if they aren't
already on your machine — this needs an internet connection once;
after that they're cached locally and it works offline.

Then open **http://127.0.0.1:5000** in your browser and start chatting.

You can also test the matching logic directly in the terminal without
the web UI:
```bash
python chatbot.py
```

## How the matching works
1. Every FAQ question is cleaned using NLTK — lowercased, tokenized
   (`word_tokenize`), stripped of punctuation and stopwords, then
   lemmatized (`WordNetLemmatizer`, e.g. "fees" -> "fee") — and turned
   into a TF-IDF vector at startup.
2. When a user asks something, their query goes through the same
   NLTK cleaning + vectorization step.
3. Cosine similarity is computed between the query vector and every
   FAQ question vector — the highest-scoring FAQ's answer is returned.
4. If the best score is below a confidence threshold (default `0.25`),
   the bot admits it isn't sure instead of returning a bad guess. Tune
   this in `FAQChatbot(confidence_threshold=...)`.

## Customizing for your own project
- Replace the contents of `faqs.json` with FAQs relevant to your chosen
  topic/product (the task just says "a topic or product").
- Adjust `confidence_threshold` in `chatbot.py` if the bot is too
  trigger-happy or too unsure.
- Want intent-matching instead of pure similarity? You could swap
  `TfidfVectorizer` for sentence embeddings (e.g. `sentence-transformers`)
  for smarter matching — worth mentioning in your project video/README
  as a possible future improvement.



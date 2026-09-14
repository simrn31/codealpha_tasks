"""
FAQ Chatbot - Core Engine
--------------------------
Task 2: Chatbot for FAQs (AI Internship Task List)

Pipeline:
1. Load FAQs (question, answer pairs).
2. Preprocess text using NLTK: tokenize, lowercase, remove punctuation
   and stopwords, then lemmatize each token.
3. Vectorize all FAQ questions using TF-IDF.
4. On a new user query -> preprocess + vectorize the same way -> compute
   cosine similarity against every FAQ question -> return the best
   match's answer.
5. If the best similarity score is below a confidence threshold, respond
   with a fallback message instead of guessing.
"""

import json
import string
from pathlib import Path

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _ensure_nltk_data():
    """
    Download the NLTK data files we need, but only if they aren't
    already present. Requires an internet connection the first time
    this runs on a given machine; after that it's cached locally.
    """
    required = {
        "tokenizers/punkt": "punkt",
        "tokenizers/punkt_tab": "punkt_tab",
        "corpora/stopwords": "stopwords",
        "corpora/wordnet": "wordnet",
        "corpora/omw-1.4": "omw-1.4",
    }
    for path, package in required.items():
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(package, quiet=True)


_ensure_nltk_data()

STOP_WORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()
PUNCT_TABLE = str.maketrans("", "", string.punctuation)


class FAQChatbot:
    def __init__(self, faq_path: str = "faqs.json", confidence_threshold: float = 0.25):
        self.faq_path = Path(faq_path)
        self.confidence_threshold = confidence_threshold
        self.faqs = self._load_faqs()
        self.questions = [item["question"] for item in self.faqs]
        self.answers = [item["answer"] for item in self.faqs]

        # Preprocess all FAQ questions once at startup.
        self.cleaned_questions = [self._preprocess(q) for q in self.questions]

        # Fit TF-IDF vectorizer on the preprocessed FAQ question corpus.
        # ngram_range=(1,2) also catches short phrases (e.g. "id card").
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.question_vectors = self.vectorizer.fit_transform(self.cleaned_questions)

    def _load_faqs(self):
        with open(self.faq_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _preprocess(text: str) -> str:
        """
        NLTK preprocessing pipeline:
        1. Lowercase
        2. Tokenize (word_tokenize)
        3. Strip punctuation tokens
        4. Remove stopwords
        5. Lemmatize (e.g. "fees" -> "fee", "applying" -> "applying"/"apply")
        """
        text = text.lower().translate(PUNCT_TABLE)
        tokens = word_tokenize(text)
        cleaned = [
            LEMMATIZER.lemmatize(tok)
            for tok in tokens
            if tok.isalpha() and tok not in STOP_WORDS
        ]
        return " ".join(cleaned) if cleaned else text.strip()

    def get_response(self, user_query: str):
        """
        Returns a dict: {answer, matched_question, score}
        so the caller (CLI or web UI) can decide how to present it.
        """
        if not user_query or not user_query.strip():
            return {
                "answer": "Please type a question and I'll do my best to help!",
                "matched_question": None,
                "score": 0.0,
            }

        cleaned_query = self._preprocess(user_query)
        query_vector = self.vectorizer.transform([cleaned_query])

        similarities = cosine_similarity(query_vector, self.question_vectors)[0]
        best_idx = similarities.argmax()
        best_score = float(similarities[best_idx])

        if best_score < self.confidence_threshold:
            return {
                "answer": (
                    "I'm not confident I have the right answer for that. "
                    "Could you rephrase, or contact the office directly for help?"
                ),
                "matched_question": None,
                "score": best_score,
            }

        return {
            "answer": self.answers[best_idx],
            "matched_question": self.questions[best_idx],
            "score": best_score,
        }

    def list_faqs(self):
        return self.faqs


if __name__ == "__main__":
    # Quick CLI test loop
    bot = FAQChatbot(faq_path=str(Path(__file__).parent / "faqs.json"))
    print("FAQ Chatbot (type 'exit' to quit)\n")
    while True:
        query = input("You: ")
        if query.strip().lower() in {"exit", "quit"}:
            break
        result = bot.get_response(query)
        print(f"Bot: {result['answer']}  (confidence: {result['score']:.2f})\n")

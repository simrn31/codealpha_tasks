"""
Flask web app for the FAQ Chatbot.
Run with: python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

from pathlib import Path
from flask import Flask, render_template, request, jsonify

from chatbot import FAQChatbot

app = Flask(__name__)
bot = FAQChatbot(faq_path=str(Path(__file__).parent / "faqs.json"))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_message = data.get("message", "")
    result = bot.get_response(user_message)
    return jsonify(result)


@app.route("/api/faqs", methods=["GET"])
def faqs():
    return jsonify(bot.list_faqs())


if __name__ == "__main__":
    app.run(debug=True, port=5000)

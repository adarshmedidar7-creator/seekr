from flask import Flask, request, render_template, redirect, jsonify
import json
import re
from collections import defaultdict
import urllib.parse
import os
import requests

app = Flask(__name__)

# ---------------- LOAD INDEX ----------------
with open("index.json", encoding="utf-8") as f:
    index = json.load(f)

with open("pages.json", encoding="utf-8") as f:
    pages = json.load(f)

# ---------------- SEARCH LOGIC ----------------
def search(query):
    words = re.findall(r"[a-zA-Z]+", query.lower())
    scores = defaultdict(int)
    snippets = {}

    for word in words:
        for page in index.get(word, []):
            count = pages[page].lower().count(word)
            scores[page] += count

            if page not in snippets and count > 0:
                text = pages[page]
                pos = text.lower().find(word)
                snippets[page] = text[max(0, pos-60):pos+120] + "..."

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(page, snippets.get(page, "")) for page, score in ranked]

# ---------------- HOME ROUTE ----------------
@app.route("/", methods=["GET"])
def home():
    q = request.args.get("q", "").strip().lower()

    # 🔥 Instant shortcuts
    shortcuts = {
        "youtube": "https://www.youtube.com",
        "yt": "https://www.youtube.com",
        "google": "https://www.google.com",
        "chatgpt": "https://chat.openai.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
        "instagram": "https://www.instagram.com"
    }

    if q in shortcuts:
        return redirect(shortcuts[q])

    if not q:
        return render_template("index.html", query="", results=[])

    results = search(q)

    # 🌍 Google fallback
    if len(results) == 0:
        google_url = "https://www.google.com/search?q=" + urllib.parse.quote(q)
        return redirect(google_url)

    return render_template("index.html", query=q, results=results)

# ---------------- SEEKR AI (OPENROUTER) ----------------
@app.route("/ai", methods=["POST"])
def seekr_ai():
    user_msg = request.json.get("message", "").strip()

    if not user_msg:
        return jsonify({"reply": "Ask me something 🙂"})

    api_key = os.getenv("OPENROUTER_API_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://seekr.onrender.com",
        "X-Title": "SEEKR AI"
    }

    payload = {
        "model": "xiaomi/mimo-v2-flash:free",
        "messages": [
            {"role": "system", "content": "You are Seekr AI, short, helpful, and clear."},
            {"role": "user", "content": user_msg}
        ]
    }

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        data = r.json()

        if "choices" not in data:
            return jsonify({"reply": "AI error. Try again later."})

        reply = data["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})

    except Exception:
        return jsonify({"reply": "Seekr AI is busy. Try again."})

# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

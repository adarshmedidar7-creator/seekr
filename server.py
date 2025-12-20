from flask import Flask, request, render_template, redirect
import json
import re
from collections import defaultdict
import urllib.parse

app = Flask(__name__)

# Load index + pages
with open("index.json", encoding="utf-8") as f:
    index = json.load(f)

with open("pages.json", encoding="utf-8") as f:
    pages = json.load(f)

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

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)

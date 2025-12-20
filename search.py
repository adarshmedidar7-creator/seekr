import json
import re
from collections import defaultdict

with open("index.json") as f:
    index = json.load(f)

with open("pages.json") as f:
    pages = json.load(f)

def search(query):
    words = re.findall(r"[a-zA-Z]+", query.lower())
    scores = defaultdict(int)

    for word in words:
        for page in index.get(word, []):
            scores[page] += pages[page].lower().count(word)

            # 🔥 title / URL bonus
            if word in page.lower():
                scores[page] += 5

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [page for page, score in ranked]

if __name__ == "__main__":
    while True:
        q = input("Search: ")
        print(search(q))

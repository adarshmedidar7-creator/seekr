import json
import re
from collections import defaultdict

with open("pages.json") as f:
    pages = json.load(f)

index = defaultdict(list)

for url, text in pages.items():
    words = re.findall(r"[a-zA-Z]+", text.lower())
    for word in set(words):
        index[word].append(url)

with open("index.json", "w") as f:
    json.dump(index, f, indent=2)

print("Index built. Total words:", len(index))

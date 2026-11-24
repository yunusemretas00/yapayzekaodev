"""Deney betiklerinin ortak yardımcıları."""
import json
import os
import platform
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from game import Game, my_game  # noqa: E402

RESULTS = os.path.join(ROOT, "results")
FIGURES = os.path.join(ROOT, "figures")
os.makedirs(RESULTS, exist_ok=True)
os.makedirs(FIGURES, exist_ok=True)


def machine_info():
    return f"{platform.processor() or platform.machine()} | Python {platform.python_version()} | {platform.system()} {platform.release()}"


def load_positions(path):
    """Her satır: boşlukla ayrılmış hamle dizisi. '#' ile başlayan satır yorum.
    Boş satır / 'empty' boş tahtayı gösterir."""
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if line == "":
                continue
            out.append("" if line.lower() == "empty" else line)
    return out


def random_positions(game, count, seed, min_moves=6, max_moves=20):
    """Seed'li rastgele hamlelerle, terminale gelmemiş konumlar (hamle dizisi olarak)."""
    rng = random.Random(seed)
    out = []
    while len(out) < count:
        target = rng.randint(min_moves, max_moves)
        s, seq = game.initial_state(), []
        ok = True
        while len(seq) < target:
            a = rng.choice(game.actions(s))
            s = game.result(s, a)
            seq.append(a)
            if game.is_terminal(s):
                ok = False
                break
        if ok:
            out.append(" ".join(map(str, seq)))
    return out


def save_json(name, obj):
    with open(os.path.join(RESULTS, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def save_text(name, text):
    with open(os.path.join(RESULTS, name), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)


def md_table(headers, rows):
    lines = ["| " + " | ".join(map(str, headers)) + " |",
             "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        lines.append("| " + " | ".join(map(str, r)) + " |")
    return "\n".join(lines)

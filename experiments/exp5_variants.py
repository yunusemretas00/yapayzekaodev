"""Aşama 5 hazırlık: beklenmedik varyantlar. Her (R, C, K) x V için ana ajan, rastgele
ajana karşı 2 oyun (bir kez önce, bir kez ikinci) oynar; yasa dışı hamle ve süre aşımı
aranır. Engelli varyant için seed = d = 7.

Kullanım: python experiments/exp5_variants.py
"""
import os
import sys

from common import ROOT, machine_info, md_table, save_text

sys.path.insert(0, ROOT)
from arena import run_series  # noqa: E402
from game import Game, VARIANT_NAMES  # noqa: E402

AGENT = f'python "{os.path.join(ROOT, "agent.py")}" --quiet'
BOARDS = [(7, 8, 5), (6, 7, 4), (5, 6, 4)]


def main():
    rows = []
    for R, C, K in BOARDS:
        for V in range(4):
            res = run_series(AGENT, AGENT + " --algo random --rng 3", 2, R, C, K, V, 7, plies=0,
                             limit=1.0, workers=2, base_seed=0)
            g = Game(R, C, K, V, d=7)
            w = sum(r["result_for_a"] == "G" for r in res)
            d = sum(r["result_for_a"] == "B" for r in res)
            bad = sum(("süre" in r["reason"]) or ("yasa dışı" in r["reason"]) or ("geçersiz" in r["reason"])
                      or ("cevap" in r["reason"]) for r in res)
            rows.append([f"{R}x{C}, K={K}", f"{V} {VARIANT_NAMES[V]}", str(g.blocked) if V == 3 else "-",
                         f"{w}/{d}/{2 - w - d}", f"{max(r['max_time_a'] for r in res):.3f}", bad])
            print(rows[-1], flush=True)
    save_text("stage5_variants.md", f"# Aşama 5: beklenmedik varyant testi (ana ajan vs rastgele, 2 oyun)\n\n"
              f"Makine: {machine_info()}\n\n"
              + md_table(["tahta", "V", "engelli hücreler", "G/B/M", "ana ajan maks süre (s)", "süre/yasa hatası"],
                         rows) + "\n")


if __name__ == "__main__":
    main()

"""Aşama 4: süre aşımı stres testi. Her aramada iki süre kontrolü arasındaki en büyük
boşluk da ölçülür: boşluk küçükken hamle uzun sürüyorsa süreç işletim sistemi
tarafından bekletilmiştir (kodun süre kontrolü değil).

Kullanım: python experiments/exp4_stress.py [--reps 2] [--limit 1.0]
"""
import argparse
import gc
import time

from common import machine_info, md_table, my_game, random_positions, save_text
from evaluate import Evaluator
from search import Searcher


class Probe(Searcher):
    def _ab(self, s, depth, alpha, beta, ext):
        if self.nodes + 1 >= self.next_check:
            now = time.perf_counter()
            self.maxgap = max(self.maxgap, now - self.last)
            self.last = now
        return Searcher._ab(self, s, depth, alpha, beta, ext)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--limit", type=float, default=1.0)
    args = ap.parse_args()
    gc.disable()
    g = my_game()
    ev = Evaluator(g)
    pos = random_positions(g, 20, seed=8080, min_moves=4, max_moves=24)
    confs = [("tablo kapalı", dict(use_tt=False)), ("tablo açık", dict(use_tt=True)),
             ("tablo + uzatma", dict(use_tt=True, extensions=4))]
    rec = []
    for _ in range(args.reps):
        for p in pos:
            s = g.play(p)
            for name, c in confs:
                S = Probe(g, ev, **c)
                S.maxgap, S.last = 0.0, time.perf_counter()
                t = time.perf_counter()
                S.search(s, time_limit=args.limit)
                rec.append((time.perf_counter() - t, S.maxgap, name))
    rows = []
    for name, _ in confs:
        R = [r for r in rec if r[2] == name]
        rows.append([name, len(R), f"{max(r[0] for r in R):.4f}", f"{1000 * max(r[1] for r in R):.1f}",
                     sum(r[0] > args.limit + 0.05 for r in R)])
    save_text("stage4_stress.md", f"# Aşama 4: süre stres testi (limit {args.limit} s)\n\nMakine: {machine_info()}\n\n"
              + md_table(["ayar", "arama", "en uzun (s)", "en büyük kontrol boşluğu (ms)", "limit+50ms aşımı"], rows) + "\n")


if __name__ == "__main__":
    main()

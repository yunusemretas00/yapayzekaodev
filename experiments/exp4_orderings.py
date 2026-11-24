"""Aşama 2/4: süre sınırında hangi sıralama? Tablo açık, uzatmasız, 1 s'de ulaşılan derinlik.

Kullanım: python experiments/exp4_orderings.py [--n 20] [--limit 1.0]
"""
import argparse
import gc
import statistics

from common import machine_info, md_table, my_game, random_positions, save_text
from evaluate import Evaluator
from search import Searcher, ORDERINGS, make_eval_order


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--limit", type=float, default=1.0)
    args = ap.parse_args()
    gc.disable()
    g = my_game()
    ev = Evaluator(g)
    eo = make_eval_order(ev)
    cfgs = [("a", dict(order=ORDERINGS["a"])), ("b", dict(order=ORDERINGS["b"])),
            ("c", dict(order=ORDERINGS["c"])), ("d", dict(order=ORDERINGS["d"])),
            ("e", dict(order=eo)), ("e (derinlik 1'de d)", dict(order=eo, order_leaf=ORDERINGS["d"]))]
    pos = random_positions(g, args.n, seed=8080, min_moves=4, max_moves=24)
    rows = []
    for name, c in cfgs:
        ds, ns = [], []
        for p in pos:
            r = Searcher(g, ev, **c).search(g.play(p), time_limit=args.limit)
            ds.append(r.depth)
            ns.append(r.nodes)
        rows.append([name, f"{statistics.mean(ds):.2f}", min(ds), max(ds), f"{statistics.mean(ns):,.0f}"])
        print(rows[-1], flush=True)
    save_text("stage4_orderings.md", f"# Süre sınırında sıralama karşılaştırması ({args.n} konum, {args.limit} s, tablo açık, "
              f"uzatmasız)\n\nMakine: {machine_info()}\n\n"
              + md_table(["sıralama", "ort. derinlik", "min", "maks", "ort. düğüm"], rows) + "\n")


if __name__ == "__main__":
    main()

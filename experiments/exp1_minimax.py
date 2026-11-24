"""Aşama 1 ölçümü: 5 konumda derinlik 2/4/6 minimax -> seçilen hamle, düğüm, süre, b_etkin.

Kullanım: python experiments/exp1_minimax.py [--pos "..."] [--depths 2 4 6] [--eval zero|full]
"""
import argparse
import os
import time

from common import ROOT, load_positions, machine_info, md_table, my_game, save_json, save_text
from search import minimax_decision, eval_zero


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pos", action="append")
    ap.add_argument("--depths", type=int, nargs="+", default=[2, 4, 6])
    ap.add_argument("--eval", choices=["zero", "full"], default="zero")
    ap.add_argument("--out", default="stage1_minimax")
    args = ap.parse_args()
    g = my_game()
    evalf = eval_zero
    if args.eval == "full":
        from evaluate import Evaluator
        evalf = Evaluator(g)
    positions = args.pos or load_positions(os.path.join(ROOT, "data", "positions_stage1.txt"))
    rows, out = [], []
    for i, p in enumerate(positions):
        s = g.play(p)
        print(f"Q{i+1}: {p}\n{g.render(s)}")
        for d in args.depths:
            t = time.perf_counter()
            a, v, nodes = minimax_decision(g, s, d, evalf)
            dt = time.perf_counter() - t
            b = nodes ** (1 / d)
            rows.append([f"Q{i+1}", d, a, f"{v:+.3f}", nodes, f"{b:.2f}", f"{dt:.2f}",
                         f"{nodes/dt/1000:.0f}"])
            out.append(dict(pos=p, depth=d, move=a, value=v, nodes=nodes, b_eff=b, sec=dt))
            print(f"  d={d}: hamle={a} değer={v:+.3f} düğüm={nodes} b_etkin={b:.2f} {dt:.2f}s")
    text = (f"# Aşama 1: minimax (eval={args.eval})\n\n{g.describe()}\n\nMakine: {machine_info()}\n\n"
            + md_table(["konum", "derinlik", "hamle", "değer", "düğüm", "b_etkin", "süre (s)", "kdüğüm/s"], rows)
            + f"\n\nC = {g.C}\n")
    save_text(args.out + ".md", text)
    save_json(args.out + ".json", out)


if __name__ == "__main__":
    main()

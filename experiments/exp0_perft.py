"""Aşama 0 ölçümü: perft tablosu (n, düğüm sayısı, süre).

Kullanım:
  python experiments/exp0_perft.py                      # boş tahta + data/positions_stage0.txt
  python experiments/exp0_perft.py --pos "3 3 4 4 5 5" --pos "0 1 2" --nmax 4
  (Kontrol noktası 0: öğretmenin verdiği konumları --pos ile verin.)
"""
import argparse
import os
import time

from common import ROOT, load_positions, machine_info, md_table, my_game, save_text, save_json
from game import perft


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pos", action="append", help="hamle dizisi (ilk hamle MAX)")
    ap.add_argument("--nmax", type=int, default=5)
    ap.add_argument("--empty-nmax", type=int, default=7)
    ap.add_argument("--out", default="stage0_perft")
    args = ap.parse_args()

    g = my_game()
    positions = args.pos if args.pos else load_positions(os.path.join(ROOT, "data", "positions_stage0.txt"))
    jobs = [("boş tahta", "", args.empty_nmax)] + [(f"P{i+1}: {p}", p, args.nmax) for i, p in enumerate(positions)]

    out, rows = [], []
    for name, seq, nmax in jobs:
        s = g.play(seq)
        print(name)
        print(g.render(s))
        for n in range(1, nmax + 1):
            t = time.perf_counter()
            cnt = perft(g, s, n)
            dt = time.perf_counter() - t
            rows.append([name, n, cnt, f"{dt:.3f}"])
            out.append({"position": seq, "n": n, "nodes": cnt, "sec": dt})
            print(f"  n={n}: {cnt}  ({dt:.3f} s)")
    text = (f"# Aşama 0: perft\n\n{g.describe()}\n\nMakine: {machine_info()}\n\n"
            + md_table(["konum", "n", "perft", "süre (s)"], rows) + "\n")
    save_text(args.out + ".md", text)
    save_json(args.out + ".json", out)


if __name__ == "__main__":
    main()

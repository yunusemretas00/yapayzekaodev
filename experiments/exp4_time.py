"""Aşama 4 ölçümleri.

A) Tablo kapalı / açık / açık + ufuk uzatması: N konumda 1 sn'de ulaşılan derinlik, düğüm, süre
B) Kontrol noktası 4: data/positions_stage4.txt'deki 10 konumda ajan ayarıyla derinlik ve süre
C) Tablo doğruluğu: Aşama 2'nin 50 konumunda derinlik 6, tablo açık ID değeri == düz α-β değeri

Kullanım: python experiments/exp4_time.py [--limit 1.0] [--n 20] [--pos-file ...]
"""
import argparse
import gc
import os
import statistics
import time

from common import FIGURES, ROOT, load_positions, machine_info, md_table, my_game, random_positions, save_json, save_text
from evaluate import Evaluator
from search import Searcher, alphabeta_value, ORDERINGS
from plotstyle import plt, SERIES
import plotstyle

CONFIGS = [("tablo kapalı", dict(use_tt=False, extensions=0)),
           ("tablo açık", dict(use_tt=True, extensions=0)),
           ("tablo açık + uzatma(4)", dict(use_tt=True, extensions=4))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=float, default=1.0)
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--pos-file", default=os.path.join(ROOT, "data", "positions_stage4.txt"))
    ap.add_argument("--skip-correctness", action="store_true")
    args = ap.parse_args()
    g = my_game()
    ev = Evaluator(g)
    gc.disable()                     # ajandaki gibi: arama sırasında çöp toplayıcı kapalı
    out = {}

    # ---------------- A
    positions = random_positions(g, args.n, seed=8080, min_moves=4, max_moves=24)
    resA = {name: [] for name, _ in CONFIGS}
    for p in positions:
        s = g.play(p)
        for name, cfg in CONFIGS:
            S = Searcher(g, ev, **cfg)
            t = time.perf_counter()
            r = S.search(s, time_limit=args.limit)
            dt = time.perf_counter() - t
            resA[name].append(dict(pos=p, depth=r.depth, nodes=r.nodes, sec=dt, move=r.move, value=r.value))
        print(p, [(n, resA[n][-1]["depth"]) for n, _ in CONFIGS])
    rows = []
    for name, _ in CONFIGS:
        R = resA[name]
        rows.append([name, f"{statistics.mean(r['depth'] for r in R):.2f}", min(r["depth"] for r in R),
                     max(r["depth"] for r in R), f"{statistics.mean(r['nodes'] for r in R):,.0f}",
                     f"{statistics.mean(r['nodes'] / r['sec'] for r in R):,.0f}",
                     f"{max(r['sec'] for r in R):.3f}"])
    out["A"] = resA
    textA = md_table(["ayar", "ort. derinlik", "min", "maks", "ort. düğüm", "düğüm/s", "en yavaş hamle (s)"], rows)

    # ---------------- B
    pos4 = load_positions(args.pos_file)
    S = Searcher(g, ev, use_tt=True, extensions=4)        # ajan ayarı (taze tablo)
    rowsB, resB = [], []
    for i, p in enumerate(pos4):
        s = g.play(p)
        t = time.perf_counter()
        r = S.search(s, time_limit=0.8)                   # ajanın iç bütçesi 0.8 s
        dt = time.perf_counter() - t
        rowsB.append([f"T{i+1}", s.n, r.move, r.depth, f"{r.value:+.3f}" if r.value is not None else "-",
                      f"{r.nodes:,}", f"{dt:.3f}"])
        resB.append(dict(pos=p, move=r.move, depth=r.depth, nodes=r.nodes, sec=dt))
    out["B"] = resB
    textB = md_table(["konum", "taş sayısı", "hamle", "derinlik", "değer", "düğüm", "süre (s)"], rowsB)

    # ---------------- C
    textC = ""
    if not args.skip_correctness:
        bad = 0
        pos2 = random_positions(g, 50, seed=4242)
        for p in pos2:
            s = g.play(p)
            ref = alphabeta_value(g, s, 6, ev, ORDERINGS["c"])
            got = Searcher(g, ev, use_tt=True).search_depth(s, 6).history[-1][2]
            bad += got != ref
        textC = f"Tablo açıkken derinlik-6 değeri düz α-β ile {50 - bad}/50 konumda aynı.\n"
        out["C_bad"] = bad

    text = (f"# Aşama 4: zaman sınırlı arama\n\nMakine: {machine_info()} (gc arama sırasında kapalı)\n\n"
            f"## A) {args.n} konum, hamle başına {args.limit} s\n\n{textA}\n\n"
            f"## B) Kontrol noktası 4: 10 konum, ajan ayarı (tablo + uzatma, iç bütçe 0.8 s)\n\n{textB}\n\n"
            f"## C) Tablo doğruluğu\n\n{textC}")
    save_text("stage4_time.md", text)
    save_json("stage4_time.json", out)

    fig, ax = plt.subplots(figsize=(6.5, 3.0))
    width = 0.27
    for j, (name, _) in enumerate(CONFIGS):
        d = [r["depth"] for r in resA[name]]
        ax.bar([i + (j - 1) * width for i in range(len(d))], d, width=width * 0.92, color=SERIES[j], label=name)
    ax.set_xlabel("konum")
    ax.set_ylabel("ulaşılan derinlik")
    ax.set_title(f"{args.limit:.0f} saniyede tamamlanan derinlik")
    ax.set_xticks(range(len(positions)))
    ax.set_xticklabels([str(i + 1) for i in range(len(positions))], fontsize=7)
    ax.legend(fontsize=7.5, ncol=3, loc="upper left")
    ax.set_ylim(0, max(r["depth"] for n, _ in CONFIGS for r in resA[n]) + 4)
    fig.tight_layout()
    fig.savefig(f"{FIGURES}/stage4_depth.png", dpi=150)


if __name__ == "__main__":
    main()

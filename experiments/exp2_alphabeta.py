"""Aşama 2 ölçümü: α-β doğruluğu ve hamle sıralaması.

* 50 rastgele konum (seed 4242, 6-20 rastgele hamle, terminal değil)
* derinlik 6'da düz minimax ile α-β (a/b/c sıralaması) kök değerleri aynı mı?
  seçilen hamlenin değeri kök değerine eşit mi?
* 50 konum x 3 sıralama ortalama düğüm sayısı -> tablo + grafik
* sıralama maliyeti: sıralama fonksiyonunun tek çağrısı (µs)

Kullanım: python experiments/exp2_alphabeta.py [--depth 6] [--eval zero|full] [--n 50]
"""
import argparse
import math
import statistics
import time

from common import FIGURES, machine_info, md_table, my_game, random_positions, save_json, save_text
from search import (ORDERINGS, Stats, alphabeta_decision, eval_zero, minimax_decision,
                    minimax_value, make_eval_order)
import plotstyle
from plotstyle import plt, SERIES

NAMES = {"a": "a: sıralamasız", "b": "b: merkezden dışarı", "c": "c: kazan/engelle + merkez",
         "d": "d: c + Misère'de kenardan içe", "e": "e: Eval tabanlı"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", type=int, default=6)
    ap.add_argument("--eval", choices=["zero", "full"], default="zero")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=4242)
    args = ap.parse_args()
    g = my_game()
    evalf = eval_zero
    if args.eval == "full":
        from evaluate import Evaluator
        evalf = Evaluator(g)
    D = args.depth
    orderings = dict(ORDERINGS)
    orderings["e"] = make_eval_order(evalf)
    KEYS = list(orderings)
    positions = random_positions(g, args.n, seed=args.seed)
    rec = []
    mismatches = 0
    for k, p in enumerate(positions):
        s = g.play(p)
        t = time.perf_counter()
        mm_a, mm_v, mm_nodes = minimax_decision(g, s, D, evalf)
        r = {"pos": p, "minimax": {"nodes": mm_nodes, "value": mm_v, "move": mm_a,
                                   "sec": time.perf_counter() - t}}
        for name, order in orderings.items():
            t = time.perf_counter()
            a, v, nodes = alphabeta_decision(g, s, D, evalf, order)
            dt = time.perf_counter() - t
            # seçilen hamlenin gerçek (minimax) değeri
            mv = minimax_value(g, g.result(s, a), D - 1, evalf, Stats()) if name == "a" or a != mm_a else mm_v
            ok = (v == mm_v) and (mv == mm_v) and nodes <= mm_nodes
            mismatches += not ok
            r[name] = {"nodes": nodes, "value": v, "move": a, "move_value": mv, "sec": dt, "ok": ok}
        rec.append(r)
        print(f"{k+1:2d}/{len(positions)} mm={mm_nodes:7d} " + " ".join(f"{x}={r[x]['nodes']:6d}" for x in KEYS)
              + f" v={mm_v:+.3f} ok={all(r[x]['ok'] for x in KEYS)}")

    # sıralama maliyeti (tek çağrı)
    cost = {}
    for name, order in orderings.items():
        reps, t = 0, time.perf_counter()
        for p in positions:
            s = g.play(p)
            acts = g.actions(s)
            for _ in range(200):
                order(g, s, acts)
                reps += 1
        cost[name] = (time.perf_counter() - t) / reps * 1e6

    mean = lambda key, f="nodes": statistics.mean(r[key][f] for r in rec)  # noqa: E731
    gmean = lambda key: math.exp(statistics.mean(math.log(r[key]["nodes"]) for r in rec))  # noqa: E731
    mm_mean = mean("minimax")
    rows = [["minimax", f"{mm_mean:,.0f}", f"{gmean('minimax'):,.0f}", "100 %",
             f"{gmean('minimax') ** (1 / D):.2f}", f"{mean('minimax', 'sec')*1000:.0f}", "-", "-"]]
    for name in KEYS:
        ratio = statistics.mean(r[name]["nodes"] / r["minimax"]["nodes"] for r in rec)
        rows.append([NAMES[name], f"{mean(name):,.0f}", f"{gmean(name):,.0f}", f"{ratio*100:.1f} %",
                     f"{gmean(name) ** (1 / D):.2f}", f"{mean(name, 'sec')*1000:.1f}",
                     f"{cost[name]:.1f}", sum(r[name]["ok"] for r in rec)])
    # kuramsal en iyi durum: minimax'ın karekökü kadar düğüm (b^(m/2))
    best_theory = statistics.mean(math.sqrt(r["minimax"]["nodes"]) for r in rec)
    worst = max(rec, key=lambda r: r["c"]["nodes"] / r["minimax"]["nodes"])
    bestc = min(rec, key=lambda r: r["c"]["nodes"] / r["minimax"]["nodes"])

    text = (f"# Aşama 2: α-β ve hamle sıralaması (derinlik {D}, eval={args.eval}, seed={args.seed})\n\n"
            f"{g.describe()}\n\nMakine: {machine_info()}\n\n"
            f"Doğruluk: {len(rec)} konumun {len(rec) - sum(1 for r in rec if not all(r[x]['ok'] for x in KEYS))}"
            f"'inde α-β değeri = minimax değeri, seçilen hamlenin değeri = kök değeri ve "
            f"α-β düğüm ≤ minimax düğüm (uyuşmazlık sayısı: {mismatches}).\n\n"
            + md_table(["yöntem", "ort. düğüm", "geom. ort.", "minimax'a oran (ort.)", "b_etkin (geom.)",
                        "ort. süre (ms)", "sıralama çağrısı (µs)", "doğru"], rows)
            + f"\n\nKuramsal en iyi sıralama ≈ sqrt(minimax düğümü) ≈ b^(m/2): ortalama {best_theory:,.0f} düğüm "
            f"(c sıralaması bunun {mean('c') / best_theory:.1f} katı).\n\n"
            f"En az budanan konum (c, oran {worst['c']['nodes'] / worst['minimax']['nodes']:.3f}): `{worst['pos']}`\n\n"
            f"En çok budanan konum (c, oran {bestc['c']['nodes'] / bestc['minimax']['nodes']:.4f}): `{bestc['pos']}`\n")
    tag = f"stage2_alphabeta_d{D}_{args.eval}"
    save_text(tag + ".md", text)
    save_json(tag + ".json", {"records": rec, "order_cost_us": cost})

    plot(rec, D, tag, KEYS)


def plot(rec, D, tag, KEYS):
    """Grafik: ortalama düğüm (log) + konum başına α-β/minimax oranı. JSON'dan da çağrılabilir."""
    mean = lambda key: statistics.mean(r[key]["nodes"] for r in rec)  # noqa: E731
    best_theory = statistics.mean(math.sqrt(r["minimax"]["nodes"]) for r in rec)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.4), gridspec_kw={"width_ratios": [1.1, 1.3]})
    labels = ["minimax"] + [f"α-β ({x})" for x in KEYS] + ["√minimax\n(kuramsal)"]
    vals = [mean("minimax")] + [mean(x) for x in KEYS] + [best_theory]
    colors = ["#898781"] + SERIES[:len(KEYS)] + ["#c3c2b7"]
    bars = ax1.bar(labels, vals, color=colors, width=0.6)
    ax1.set_yscale("log")
    ax1.set_title(f"Ortalama düğüm sayısı (derinlik {D}, {len(rec)} konum)")
    for b_, v in zip(bars, vals):
        ax1.text(b_.get_x() + b_.get_width() / 2, v * 1.15, f"{v:,.0f}", ha="center", fontsize=7, color=plotstyle.INK2)
    ax1.set_ylim(top=max(vals) * 4)
    ax1.tick_params(axis="x", labelsize=7)
    order_idx = sorted(range(len(rec)), key=lambda i: rec[i]["minimax"]["nodes"])
    for j, name in enumerate(KEYS):
        ax2.plot(range(len(rec)), [rec[i][name]["nodes"] / rec[i]["minimax"]["nodes"] for i in order_idx],
                 "o", ms=3.5, color=SERIES[j], label=NAMES[name])
    ax2.set_yscale("log")
    ax2.set_xlabel("konum (minimax düğüm sayısına göre sıralı)")
    ax2.set_title("α-β düğüm / minimax düğüm")
    ax2.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    fig.savefig(f"{FIGURES}/{tag}.png", dpi=150)
    plt.close(fig)
    print("grafik:", f"{FIGURES}/{tag}.png")


if __name__ == "__main__":
    main()

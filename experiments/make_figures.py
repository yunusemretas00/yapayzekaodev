"""Rapor grafikleri: results/*.json dosyalarından (aramayı yeniden çalıştırmadan) üretir.

Kullanım: python experiments/make_figures.py
"""
import json
import math
import os
from collections import defaultdict

from common import FIGURES, RESULTS
from plotstyle import plt, SERIES, INK2


def load(name):
    p = os.path.join(RESULTS, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def fig_stage01():
    p0, p1 = load("stage0_perft.json"), load("stage1_minimax.json")
    fig, (a, b) = plt.subplots(1, 2, figsize=(9, 3.1))
    if p0:
        by = defaultdict(list)
        for r in p0:
            by[r["position"] or "boş tahta"].append((r["n"], r["nodes"]))
        for j, (k, v) in enumerate(by.items()):
            lab = k if k == "boş tahta" else f"P{j}"
            a.plot([x for x, _ in v], [y for _, y in v], "o-", ms=4, color=SERIES[j], label=lab)
        ns = range(1, 8)
        a.plot(ns, [8 ** n for n in ns], ":", color="#898781", lw=1.2, label="C^n")
        a.set_yscale("log")
        a.set_xlabel("n")
        a.set_title("Perft (yaprak sayısı)")
        a.legend(fontsize=7)
    if p1:
        by = defaultdict(list)
        for r in p1:
            by[r["pos"]].append((r["depth"], r["nodes"]))
        for j, (k, v) in enumerate(by.items()):
            b.plot([x for x, _ in v], [y for _, y in v], "o-", ms=4, color=SERIES[j], label=f"Q{j + 1}")
        ds = [2, 4, 6]
        b.plot(ds, [sum(8 ** i for i in range(d + 1)) for d in ds], ":", color="#898781", lw=1.2,
               label="1+C+…+C^d")
        b.set_yscale("log")
        b.set_xticks(ds)
        b.set_xlabel("derinlik")
        b.set_title("Minimax düğüm sayısı")
        b.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(f"{FIGURES}/stage01.png", dpi=150)
    plt.close(fig)


def fig_stage3():
    res = load("stage3_weights_d5.json")
    if not res:
        return
    names = ["A", "B", "C"]
    wins = {n: [0, 0, 0] for n in names}       # galibiyet, beraberlik, mağlubiyet
    for r in res:
        a, b = r["first"], r["second"]
        if r["winner"] == 1:
            wins[a][0] += 1
            wins[b][2] += 1
        elif r["winner"] == 2:
            wins[b][0] += 1
            wins[a][2] += 1
        else:
            wins[a][1] += 1
            wins[b][1] += 1
    fig, ax = plt.subplots(figsize=(5, 2.2))
    left = [0] * 3
    for k, (lab, col) in enumerate(zip(["galibiyet", "beraberlik", "mağlubiyet"],
                                       [SERIES[2], "#c3c2b7", SERIES[7]])):
        vals = [wins[n][k] for n in names]
        ax.barh(names, vals, left=left, color=col, label=lab, height=0.55, edgecolor="#fcfcfb", linewidth=2)
        for i, v in enumerate(vals):
            if v:
                ax.text(left[i] + v / 2, i, str(v), ha="center", va="center", fontsize=8,
                        color="#ffffff" if k != 1 else "#0b0b0b")
        left = [l + v for l, v in zip(left, vals)]
    ax.invert_yaxis()
    ax.set_xlabel("oyun (her vektör 40 oyun)")
    ax.set_title("Ağırlık vektörleri: derinlik 5 α-β, 60 oyun")
    ax.legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.01, 1.0))
    fig.savefig(f"{FIGURES}/stage3_weights.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_stage5():
    res = load("stage5_tournament.json")
    if not res:
        return
    names = list(res)
    fig, ax = plt.subplots(figsize=(6.5, 2.6))
    left = [0] * len(names)
    for k, (key, lab, col) in enumerate(zip("GBM", ["galibiyet", "beraberlik", "mağlubiyet"],
                                            [SERIES[2], "#c3c2b7", SERIES[7]])):
        vals = [sum(r["result_for_a"] == key for r in res[n]) for n in names]
        ax.barh(names, vals, left=left, color=col, label=lab, height=0.6, edgecolor="#fcfcfb", linewidth=2)
        for i, v in enumerate(vals):
            if v:
                ax.text(left[i] + v / 2, i, str(v), ha="center", va="center", fontsize=7.5,
                        color="#ffffff" if k != 1 else "#0b0b0b")
        left = [l + v for l, v in zip(left, vals)]
    ax.invert_yaxis()
    ax.tick_params(axis="y", labelsize=7.5)
    ax.set_xlabel("oyun")
    ax.set_title("Ana ajanın sonuçları (1 s/hamle, gerçek süreçler)")
    ax.legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.01, 1.0))
    fig.savefig(f"{FIGURES}/stage5_tournament.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    # hamle süreleri dağılımı
    times = [t for n in names for r in res[n] for t in r["times"]["1" if r["a_first"] else "2"]]
    if times:
        fig, ax = plt.subplots(figsize=(5, 2.2))
        ax.hist(times, bins=40, color=SERIES[0])
        ax.axvline(1.0, color=SERIES[7], lw=1.5)
        ax.text(0.99, ax.get_ylim()[1] * 0.85, "sınır 1 s", ha="right", fontsize=7.5, color=INK2)
        ax.set_xlabel("ana ajan hamle süresi (s, hakemin ölçtüğü duvar saati)")
        ax.set_title(f"{len(times)} hamle, en yavaş {max(times):.3f} s")
        fig.tight_layout()
        fig.savefig(f"{FIGURES}/stage5_times.png", dpi=150)
        plt.close(fig)


if __name__ == "__main__":
    fig_stage01()
    fig_stage3()
    fig_stage5()
    print("tamam")

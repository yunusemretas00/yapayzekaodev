"""Aşama 5: yerel turnuva (gerçek süreçler + föydeki protokol, hamle başına 1 s) ve
yenilgi analizi. Ana ajan = python agent.py (α-β, tablo, sıralama d, uzatma 4, ağırlık A).

Kullanım: python experiments/exp5_tournament.py [--games 10] [--workers 5]
"""
import argparse
import json
import os
import sys
import time

from common import ROOT, RESULTS, machine_info, md_table, my_game, save_text

sys.path.insert(0, ROOT)
from arena import run_series  # noqa: E402
from evaluate import Evaluator  # noqa: E402
from search import Searcher  # noqa: E402

AGENT = f'python "{os.path.join(ROOT, "agent.py")}" --quiet'
MAIN = AGENT
OPPONENTS = [
    ("Rastgele", AGENT + " --algo random --rng 1", 10),
    ("Derinlik 2 α-β", AGENT + " --depth 2 --ext 0", 10),
    ("Föy ayarı: sıralama c, uzatmasız", AGENT + " --order c --ext 0", 10),
    ("Uzatmasız (sıralama d)", AGENT + " --ext 0", 10),
    ("Ağırlık C", AGENT + " --weights C", 10),
    ("MCTS (bonus)", AGENT + " --algo mcts --rng 1", 20),
]


def analyse_loss(rec, a_player, secs=6.0):
    """Kaybedilen oyunda ana ajanın her hamlesini derin aramayla (ID, 'secs' saniye)
    yeniden değerlendirir. Konum henüz kaybedilmemişken (değer > -1, ajanın gözüyle)
    seçilen hamle kanıtlanmış kayba (-1) götürüyorsa ilk hata odur."""
    g = my_game()
    ev = Evaluator(g)
    sign = 1 if a_player == 1 else -1
    rows, first_err = [], None
    s = g.play(rec["opening"])
    for k in range(len(rec["opening"]), len(rec["moves"])):
        a = rec["moves"][k]
        if s.to_move == a_player:
            S = Searcher(g, ev, extensions=4)
            r = S.search(s, time_limit=secs)
            child = g.result(s, a)
            if g.is_terminal(child):
                cv, cd = g.utility(child), 0
            else:
                rc = Searcher(g, ev, extensions=4).search(child, time_limit=secs)
                cv, cd = rc.value if rc.value is not None else rc.history[-1][2] if rc.history else 0.0, rc.depth
            pv = r.value if r.value is not None else 0.0
            rows.append([k + 1, a, f"{pv * sign:+.3f}", r.depth, r.move, f"{cv * sign:+.3f}", cd])
            if first_err is None and pv * sign > -1 and cv * sign <= -1:
                first_err = dict(ply=k + 1, played=a, best=r.move, best_value=pv * sign, depth=r.depth,
                                 seq=" ".join(map(str, rec["moves"][:k])))
        s = g.result(s, a)
    return rows, first_err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=None, help="her rakip için oyun sayısını ezer")
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--skip-analysis", action="store_true")
    ap.add_argument("--only", nargs="+", default=None,
                    help="yalnız bu rakip(ler)i yeniden oynat, diğerlerini mevcut JSON'dan al")
    args = ap.parse_args()
    g = my_game()
    allres = {}
    old = {}
    if args.only:
        with open(os.path.join(RESULTS, "stage5_tournament.json"), encoding="utf-8") as f:
            old = json.load(f)
    t0 = time.perf_counter()
    for name, cmd, n in OPPONENTS:
        if args.only and name not in args.only:
            allres[name] = old[name]
            continue
        n = args.games or n
        res = run_series(MAIN, cmd, n, g.R, g.C, g.K, g.V, g.d, plies=2, limit=1.0,
                         workers=args.workers, base_seed=900, label_a="Ana ajan", label_b=name)
        allres[name] = res
        w = sum(r["result_for_a"] == "G" for r in res)
        d = sum(r["result_for_a"] == "B" for r in res)
        print(f"{name}: G {w} B {d} M {len(res) - w - d}  ({time.perf_counter() - t0:.0f} s)", flush=True)
    with open(os.path.join(RESULTS, "stage5_tournament.json"), "w", encoding="utf-8") as f:
        json.dump(allres, f, ensure_ascii=False)

    rows = []
    max_a = 0.0
    timeouts = illegal = 0
    for name, res in allres.items():
        w = sum(r["result_for_a"] == "G" for r in res)
        d = sum(r["result_for_a"] == "B" for r in res)
        wf = sum(r["result_for_a"] == "G" and r["a_first"] for r in res)
        ws = sum(r["result_for_a"] == "G" and not r["a_first"] for r in res)
        ma = max(r["max_time_a"] for r in res)
        max_a = max(max_a, ma)
        timeouts += sum("süreyi aştı" in r["reason"] for r in res)
        illegal += sum("yasa dışı" in r["reason"] or "geçersiz" in r["reason"] for r in res)
        avg_len = sum(len(r["moves"]) for r in res) / len(res)
        rows.append([name, len(res), w, d, len(res) - w - d, f"{wf}/{ws}", f"{avg_len:.1f}", f"{ma:.3f}",
                     f"{max(r['max_time_b'] for r in res):.3f}"])
    text = (f"# Aşama 5: yerel turnuva (hamle başına 1 s, gerçek süreçler, ilk 2 hamle seed'li rastgele, "
            f"seed 900+i//2)\n\nMakine: {machine_info()} ({args.workers} oyun paralel)\n\n"
            + md_table(["rakip", "oyun", "G", "B", "M", "G (önce/ikinci)", "ort. hamle", "ana ajan maks süre (s)",
                        "rakip maks süre (s)"], rows)
            + f"\n\nAna ajanın en yavaş hamlesi: {max_a:.3f} s (soğuk başlatma dahil). Süre aşımı: {timeouts}, "
              f"yasa dışı/geçersiz hamle: {illegal}.\n")

    # ---------------- yenilgi analizi
    if not args.skip_analysis:
        lost = [(name, r) for name, res in allres.items() for r in res if r["result_for_a"] == "M"]
        text += f"\n## Kaybedilen oyunlar ({len(lost)})\n\n"
        for name, r in lost:
            text += f"* {name}, oyun {r['game']} (ana ajan {'önce' if r['a_first'] else 'ikinci'}): `{' '.join(map(str, r['moves']))}` — {r['reason']}\n"
        if lost:
            name, r = lost[0]
            a_player = 1 if r["a_first"] else 2
            rows2, err = analyse_loss(r, a_player)
            text += (f"\n### Analiz: {name}, oyun {r['game']}\n\n"
                     "Her ana ajan hamlesi için 6 s'lik derin arama (değerler ana ajanın gözüyle):\n\n"
                     + md_table(["hamle no", "oynanan", "konum değeri", "derinlik", "derin aramanın hamlesi",
                                 "oynanan hamle sonrası değer", "derinlik"], rows2) + "\n\n")
            if err:
                s = g.play(err["seq"])
                text += (f"İlk hata: {err['ply']}. hamle ({err['played']} oynandı; derin arama {err['best']} "
                         f"öneriyor, değer {err['best_value']:+.3f}, derinlik {err['depth']}).\n\n"
                         f"```\n{g.render(s)}\n```\n")
            else:
                text += "Derin arama kanıtlanmış bir 'ilk hata' bulamadı (kayıp Eval'in yavaş yavaş yanılmasından).\n"
    save_text("stage5_tournament.md", text)


if __name__ == "__main__":
    main()

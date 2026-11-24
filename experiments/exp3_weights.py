"""Aşama 3 ağırlık ayarı: 3 ağırlık vektörü, her çift her iki yönde 10'ar oyun,
iki taraf da derinlik 5 α-β (sıralama c). Çeşitlilik: ilk 4 hamle seed'li rastgele
(oyun i için seed = SEED + i); aynı açılış iki yönde de oynanır (eşli tasarım).

Kullanım: python experiments/exp3_weights.py [--games 10] [--depth 5] [--sets A B C]
"""
import argparse
import itertools
import os
import time
from multiprocessing import Pool

from common import machine_info, md_table, my_game, save_json, save_text
from match import play_game, random_opening
from evaluate import Evaluator, WEIGHT_SETS
from search import alphabeta_decision, ORDERINGS

SEED = 3000
PRED = {  # oynatmadan ÖNCE yazılan tahmin (rapordaki "tahmin" sütunu)
    "A": "en iyi ya da C ile başa baş",
    "B": "en kötü (Misère'de standart işaretler kendini dizmeye iter)",
    "C": "A'ya yakın; zugzwang sonlarında daha iyi",
}


def make_agent(game, wname, depth):
    ev = Evaluator(game, WEIGHT_SETS[wname])
    order = ORDERINGS["c"]

    def agent(g, s):
        return alphabeta_decision(g, s, depth, ev, order)[0]
    return agent


def run_one(job):
    wx, wy, i, depth, plies = job          # wx önce başlar (MAX)
    g = my_game()
    opening = random_opening(g, plies, SEED + i)
    t = time.perf_counter()
    r = play_game(g, make_agent(g, wx, depth), make_agent(g, wy, depth), opening)
    return {"first": wx, "second": wy, "game": i, "opening": opening, "winner": r["winner"],
            "moves": r["moves"], "sec": time.perf_counter() - t,
            "max_move_sec": max(r["times"][1] + r["times"][2])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=10)
    ap.add_argument("--depth", type=int, default=5)
    ap.add_argument("--plies", type=int, default=4)
    ap.add_argument("--sets", nargs="+", default=["A", "B", "C"])
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    args = ap.parse_args()
    jobs = []
    for x, y in itertools.combinations(args.sets, 2):
        for i in range(args.games):
            jobs.append((x, y, i, args.depth, args.plies))
            jobs.append((y, x, i, args.depth, args.plies))
    t0 = time.perf_counter()
    with Pool(args.workers) as pool:
        res = []
        for r in pool.imap_unordered(run_one, jobs):
            res.append(r)
            print(f"{len(res)}/{len(jobs)} {r['first']}-{r['second']} oyun {r['game']}: kazanan "
                  f"{ {1: r['first'], 2: r['second'], 0: 'beraberlik'}[r['winner']] } ({len(r['moves'])} hamle)")
    total = time.perf_counter() - t0

    names = args.sets
    win = {(a, b): 0 for a in names for b in names}
    draw = {(a, b): 0 for a in names for b in names}
    first_wins = second_wins = draws = 0
    for r in res:
        a, b = r["first"], r["second"]
        if r["winner"] == 1:
            win[(a, b)] += 1
            first_wins += 1
        elif r["winner"] == 2:
            win[(b, a)] += 1
            second_wins += 1
        else:
            draw[(a, b)] += 1
            draw[(b, a)] += 1
            draws += 1
    n = 2 * args.games
    rows = []
    for a in names:
        row = [f"**{a}**"]
        tot = 0
        for b in names:
            if a == b:
                row.append("—")
            else:
                row.append(f"{win[(a, b)]} G / {draw[(a, b)]} B / {n - win[(a, b)] - draw[(a, b)]} M")
                tot += win[(a, b)]
        row += [tot, PRED[a] if a in PRED else ""]
        rows.append(row)
    wtab = md_table(["ağırlık"] + ["f1", "f2", "f3", "f4", "f5", "f6"],
                    [[k] + [f"{WEIGHT_SETS[k][f]:+.2f}" for f in ["f1", "f2", "f3", "f4", "f5", "f6"]] for k in names])
    text = (f"# Aşama 3: ağırlık ayarı (derinlik {args.depth} α-β, sıralama c, ilk {args.plies} hamle rastgele, "
            f"seed = {SEED}+i)\n\nMakine: {machine_info()}\n\nAğırlık vektörleri:\n\n{wtab}\n\n"
            f"Satır = ağırlık vektörü, sütun = rakip, hücre = satırın {n} oyundaki galibiyet/beraberlik/mağlubiyeti "
            f"({args.games} oyun önce başlayarak + {args.games} oyun ikinci).\n\n"
            + md_table(["vektör"] + names + ["toplam galibiyet", "tahmin"], rows)
            + f"\n\nİlk başlayan kazandı: {first_wins}, ikinci kazandı: {second_wins}, beraberlik: {draws} "
              f"(toplam {len(res)} oyun, {total:.0f} s duvar saati, {args.workers} paralel süreç).\n"
              f"En yavaş hamle: {max(r['max_move_sec'] for r in res):.2f} s.\n")
    save_text(f"stage3_weights_d{args.depth}.md", text)
    save_json(f"stage3_weights_d{args.depth}.json", res)


if __name__ == "__main__":
    main()

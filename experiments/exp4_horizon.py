"""Aşama 4.3: ufuk etkisi.

1) Sabit derinlik D0 (uzatmasız) ajan kendine karşı oynar (seed'li rastgele açılışlar).
   Her hamlesi derinlik DEEP'lik bir doğrulayıcı aramayla kontrol edilir: seçilen hamle
   sırası gelen için KANITLANMIŞ KAYBA (±1) gidiyor ama konumda kaybetmeyen bir hamle
   varsa -> derinlik sınırı yüzünden yapılmış kötü hamle (ufuk etkisi).
2) Bulunan konumda derinlik D0, D0+1, ..., DEEP'te seçilen hamle ve değer (kanıt).
3) Düzeltme: sakin olmayan konumlarda aramayı uzatma (extensions). Aynı konumda D0 + uzatma.
4) Önce/sonra: D0 uzatmasız vs D0 uzatmalı maç (eşli açılışlar) + kötü hamle sayısı.

Kullanım: python experiments/exp4_horizon.py [--d0 4] [--deep 9] [--games 12] [--ext 4]
"""
import argparse
import os
import time
from multiprocessing import Pool

from common import machine_info, md_table, my_game, save_json, save_text
from match import random_opening
from evaluate import Evaluator
from search import Searcher

SEED = 7000


def fixed(g, ev, depth, ext):
    S = Searcher(g, ev, extensions=ext)
    return lambda s: S.search(s, time_limit=1e9, max_depth=depth)


def deep_value(g, ev, s, deep):
    return Searcher(g, ev).fixed_depth(s, deep)[1]


def blunder_check(g, ev, s, move, deep):
    """Hamle mover için kanıtlanmış kayıp mı ve kaçınılabilir miydi?"""
    sign = 1 if s.to_move == 1 else -1
    child = g.result(s, move)
    cv = deep_value(g, ev, child, deep)
    if cv * sign > -1:
        return None
    deep_move, best_v = Searcher(g, ev).fixed_depth(s, deep)
    if best_v * sign <= -1:
        return None                       # zaten kayıp konum: hata sayılmaz
    return {"child_value": cv, "deep_move": deep_move, "deep_value": best_v}


def worker(job):
    kind, i, d0, deep, ext = job
    g = my_game()
    ev = Evaluator(g)
    opening = random_opening(g, 4, SEED + i)
    s = g.play(opening)
    moves = list(opening)
    if kind == "selfplay":
        agents = {1: fixed(g, ev, d0, 0), 2: fixed(g, ev, d0, 0)}
    elif kind == "noext_first":
        agents = {1: fixed(g, ev, d0, 0), 2: fixed(g, ev, d0, ext)}
    else:
        agents = {1: fixed(g, ev, d0, ext), 2: fixed(g, ev, d0, 0)}
    blunders = []
    nodes = {1: 0, 2: 0}
    secs = {1: 0.0, 2: 0.0}
    while not g.is_terminal(s):
        t = time.perf_counter()
        r = agents[s.to_move](s)
        secs[s.to_move] += time.perf_counter() - t
        nodes[s.to_move] += r.nodes
        b = blunder_check(g, ev, s, r.move, deep)
        if b:
            b.update(seq=" ".join(map(str, moves)), move=r.move, player=s.to_move, value=r.value)
            blunders.append(b)
        s = g.result(s, r.move)
        moves.append(r.move)
    return {"kind": kind, "game": i, "winner": g.winner(s), "moves": moves,
            "blunders": blunders, "nodes": nodes, "secs": secs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d0", type=int, default=4)
    ap.add_argument("--deep", type=int, default=9)
    ap.add_argument("--games", type=int, default=12)
    ap.add_argument("--ext", type=int, default=4)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 3))
    args = ap.parse_args()
    g = my_game()
    ev = Evaluator(g)
    jobs = [("selfplay", i, args.d0, args.deep, args.ext) for i in range(args.games)]
    jobs += [("noext_first", i, args.d0, args.deep, args.ext) for i in range(args.games)]
    jobs += [("ext_first", i, args.d0, args.deep, args.ext) for i in range(args.games)]
    with Pool(args.workers) as pool:
        res = pool.map(worker, jobs)

    # ---- 1-3: kendi kendine oyunlardaki ilk kötü hamle + derinlik taraması
    examples = []
    for r in res:
        if r["kind"] != "selfplay":
            continue
        for b in r["blunders"]:
            s = g.play(b["seq"])
            scan = []
            for d in range(args.d0, args.deep + 1):
                scan.append((d,) + Searcher(g, ev).fixed_depth(s, d))
            fx = Searcher(g, ev, extensions=args.ext).search(s, time_limit=1e9, max_depth=args.d0)
            fixed_ok = blunder_check(g, ev, s, fx.move, args.deep) is None
            examples.append(dict(b, scan=scan, ext_move=fx.move, ext_value=fx.value, ext_fixes=fixed_ok,
                                 game=r["game"]))
    examples.sort(key=lambda e: (not e["ext_fixes"], len(e["seq"])))
    ex = examples[0] if examples else None

    text = f"# Aşama 4.3: ufuk etkisi (D0 = {args.d0}, doğrulayıcı derinlik = {args.deep}, uzatma = {args.ext})\n\n"
    text += f"Makine: {machine_info()}\n\n"
    text += (f"Kendi kendine {args.games} oyunda bulunan kötü hamle (kanıtlanmış kayba giden, kaçınılabilir): "
             f"{len(examples)}; bunların {sum(e['ext_fixes'] for e in examples)} tanesini uzatma düzeltiyor.\n\n")
    if ex:
        s = g.play(ex["seq"])
        who = "MAX (X)" if ex["player"] == 1 else "MIN (O)"
        text += f"## Örnek konum (sıra {who}'da)\n\nHamle dizisi: `{ex['seq']}`\n\n```\n{g.render(s)}\n```\n\n"
        text += md_table(["derinlik", "seçilen hamle", "kök değeri (MAX gözüyle)"],
                         [[d, m, f"{v:+.3f}"] for d, m, v in ex["scan"]])
        text += (f"\n\nD0 = {args.d0}'te seçilen {ex['move']}, derinlik {args.deep} doğrulamasında "
                 f"{ex['child_value']:+.0f} (kanıtlanmış kayıp). Doğru hamle {ex['deep_move']} "
                 f"(değer {ex['deep_value']:+.3f}).\n\nD0 = {args.d0} + uzatma({args.ext}) ile seçilen hamle: "
                 f"{ex['ext_move']} (değer {ex['ext_value']:+.3f}) -> "
                 f"{'kötü hamleden kaçınıyor' if ex['ext_fixes'] else 'hâlâ kötü'}.\n\n")
    # ---- 4: önce/sonra
    w_ext = w_no = dr = 0
    bl_ext = bl_no = 0
    nodes_ext = nodes_no = moves_ext = moves_no = 0
    sec_ext = sec_no = 0.0
    for r in res:
        if r["kind"] == "selfplay":
            continue
        ext_player = 2 if r["kind"] == "noext_first" else 1
        no_player = 3 - ext_player
        if r["winner"] == ext_player:
            w_ext += 1
        elif r["winner"] == no_player:
            w_no += 1
        else:
            dr += 1
        bl_ext += sum(b["player"] == ext_player for b in r["blunders"])
        bl_no += sum(b["player"] == no_player for b in r["blunders"])
        nodes_ext += r["nodes"][ext_player]
        nodes_no += r["nodes"][no_player]
        sec_ext += r["secs"][ext_player]
        sec_no += r["secs"][no_player]
        n_ext = sum(1 for k in range(4, len(r["moves"])) if (k % 2 == 0) == (ext_player == 1))
        moves_ext += n_ext
        moves_no += len(r["moves"]) - 4 - n_ext
    text += f"## Önce / sonra (derinlik {args.d0}, {2 * args.games} oyun, eşli açılışlar)\n\n"
    text += md_table(["ajan", "galibiyet", "kötü hamle sayısı", "hamle başına düğüm", "hamle başına süre (ms)"],
                     [["uzatmasız (önce)", w_no, bl_no, f"{nodes_no / max(1, moves_no):,.0f}",
                       f"{1000 * sec_no / max(1, moves_no):.0f}"],
                      [f"uzatma={args.ext} (sonra)", w_ext, bl_ext, f"{nodes_ext / max(1, moves_ext):,.0f}",
                       f"{1000 * sec_ext / max(1, moves_ext):.0f}"]])
    text += f"\n\nBeraberlik: {dr}.\n"
    save_text("stage4_horizon.md", text)
    save_json("stage4_horizon.json", {"examples": examples, "games": res})


if __name__ == "__main__":
    main()

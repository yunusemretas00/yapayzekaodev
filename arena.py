"""Yerel hakem: iki ajan SÜRECİNİ föydeki protokolle (MOVES ... / QUIT) oynatır.

Her hamlenin süresi, hakemin MOVES satırını yazmasından cevabı okumasına kadar geçen
duvar saati süresidir (süreç başlatma + ilk hamlede Python'un açılışı DAHİL; en kötü
durum). Süreyi (--limit) aşan ya da yasa dışı hamle yapan taraf o oyunu kaybeder.

Tek maç:
  python arena.py --a "python agent.py" --b "python agent.py --algo random" --games 4
"""
import argparse
import json
import queue
import random
import shlex
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from game import Game, MY_R, MY_C, MY_K, MY_V, MY_D


class AgentProc:
    def __init__(self, cmd, variant_args):
        args = shlex.split(cmd, posix=True) + variant_args
        if args[0] == "python":
            args[0] = sys.executable
        self.p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, text=True, bufsize=1)
        self.q = queue.Queue()
        threading.Thread(target=self._reader, daemon=True).start()

    def _reader(self):
        for line in self.p.stdout:
            self.q.put(line)
        self.q.put(None)

    def ask(self, moves, hard_timeout):
        t = time.perf_counter()
        self.p.stdin.write("MOVES " + " ".join(map(str, moves)) + "\n")
        self.p.stdin.flush()
        try:
            line = self.q.get(timeout=hard_timeout)
        except queue.Empty:
            return None, time.perf_counter() - t
        return line, time.perf_counter() - t

    def close(self):
        try:
            self.p.stdin.write("QUIT\n")
            self.p.stdin.flush()
            self.p.wait(timeout=2)
        except Exception:
            self.p.kill()


def play(cmd_first, cmd_second, R, C, K, V, seed, opening=(), limit=1.0):
    """Dönüş: dict(winner 1/2/0, reason, moves, times{1:[...],2:[...]})"""
    game = Game(R, C, K, V, d=seed)
    vargs = ["--R", str(R), "--C", str(C), "--K", str(K), "--V", str(V), "--seed", str(seed)]
    procs = {1: AgentProc(cmd_first, vargs), 2: AgentProc(cmd_second, vargs)}
    s = game.play(list(opening))
    moves = list(opening)
    times = {1: [], 2: []}
    winner, reason = None, ""
    try:
        while not game.is_terminal(s):
            p = s.to_move
            line, dt = procs[p].ask(moves, hard_timeout=limit + 3.0)
            times[p].append(dt)
            if line is None:
                winner, reason = 3 - p, f"oyuncu {p} cevap vermedi"
                break
            if dt > limit:
                winner, reason = 3 - p, f"oyuncu {p} süreyi aştı ({dt:.3f} s)"
                break
            try:
                a = int(line.strip())
            except ValueError:
                winner, reason = 3 - p, f"oyuncu {p} geçersiz çıktı: {line!r}"
                break
            if a not in game.actions(s):
                winner, reason = 3 - p, f"oyuncu {p} yasa dışı hamle: {a}"
                break
            s = game.result(s, a)
            moves.append(a)
        if winner is None:
            winner = game.winner(s)
            if s.liner:
                reason = f"oyuncu {s.liner} K'lık dizi yaptı" + (" (Misère: kaybeder)" if V == 2 else "")
            else:
                reason = "tahta doldu"
    finally:
        for pr in procs.values():
            pr.close()
    return {"winner": winner, "reason": reason, "moves": moves, "opening": list(opening), "times": times}


def run_series(cmd_a, cmd_b, games, R, C, K, V, seed, plies=2, limit=1.0, workers=4, base_seed=500,
               label_a="A", label_b="B"):
    """games oyun: yarısında A başlar, yarısında B; açılışlar eşli (i//2)."""
    game = Game(R, C, K, V, d=seed)
    jobs = []
    for i in range(games):
        rng = random.Random(base_seed + i // 2)
        s, op = game.initial_state(), []
        for _ in range(plies):
            a = rng.choice(game.actions(s))
            s = game.result(s, a)
            op.append(a)
        a_first = i % 2 == 0
        jobs.append((i, a_first, op))

    def one(job):
        i, a_first, op = job
        first, second = (cmd_a, cmd_b) if a_first else (cmd_b, cmd_a)
        r = play(first, second, R, C, K, V, seed, op, limit)
        a_player = 1 if a_first else 2
        r.update(game=i, a_first=a_first, label_a=label_a, label_b=label_b,
                 result_for_a="G" if r["winner"] == a_player else ("B" if r["winner"] == 0 else "M"),
                 max_time_a=max(r["times"][a_player], default=0),
                 max_time_b=max(r["times"][3 - a_player], default=0))
        return r

    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(one, jobs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", default="python agent.py")
    ap.add_argument("--b", default="python agent.py --algo random")
    ap.add_argument("--games", type=int, default=4)
    ap.add_argument("--R", type=int, default=MY_R)
    ap.add_argument("--C", type=int, default=MY_C)
    ap.add_argument("--K", type=int, default=MY_K)
    ap.add_argument("--V", type=int, default=MY_V)
    ap.add_argument("--seed", type=int, default=MY_D)
    ap.add_argument("--plies", type=int, default=2)
    ap.add_argument("--limit", type=float, default=1.0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    res = run_series(args.a, args.b, args.games, args.R, args.C, args.K, args.V, args.seed,
                     args.plies, args.limit, args.workers)
    for r in res:
        print(f"oyun {r['game']}: A {'önce' if r['a_first'] else 'ikinci'} -> A için {r['result_for_a']} "
              f"({r['reason']}, {len(r['moves'])} hamle, A maks {r['max_time_a']:.3f} s, B maks {r['max_time_b']:.3f} s)")
    print("A: G/B/M =", sum(r["result_for_a"] == "G" for r in res), sum(r["result_for_a"] == "B" for r in res),
          sum(r["result_for_a"] == "M" for r in res))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

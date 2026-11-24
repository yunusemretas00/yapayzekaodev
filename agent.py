"""Aşama 5: komut satırı ajanı.

    python agent.py --R 6 --C 7 --K 4 --V 2 --seed 7

Standart girdiden satır satır komut okur:
    MOVES 3 3 4   -> şu ana kadarki hamleler; sıra bizde. Standart çıktıya bir sütun yazar.
    QUIT          -> program kapanır.
Hata ayıklama çıktısı yalnızca stderr'e yazılır (--quiet ile kapatılır).

--seed, föydeki engelli hücre çekimi için kullanılan d'dir (rng = random.Random(seed)).
Parametre verilmezse benim varyantım (R=5, C=8, K=4, V=2, d=42) kullanılır.

Güvenlik: süre bütçesi satır OKUNDUĞU anda başlar (ilk komutta 0.55 s, sonra 0.8 s); arama içeride en geç bütçe dolunca
durur ve son tamamlanan derinliğin hamlesini verir. Herhangi bir hata olursa yasal bir
yedek hamle (merkeze en yakın boş sütun) yazılır; program asla çökmez/sessiz kalmaz.
"""
import argparse
import gc
import sys
import time

from game import Game, MY_R, MY_C, MY_K, MY_V, MY_D
from evaluate import Evaluator, WEIGHT_SETS
from search import Searcher, ORDERINGS, center_order


def log(*a):
    if not ARGS.quiet:
        print(*a, file=sys.stderr, flush=True)


def build_player(game, args):
    """(state, time_budget) -> (hamle, bilgi metni)"""
    if args.algo == "random":
        import random
        rng = random.Random(args.rng)
        return lambda s, budget: (rng.choice(game.actions(s)), "random")
    if args.algo == "mcts":
        from mcts import MCTS
        m = MCTS(game, seed=args.rng)

        def play_mcts(s, budget):
            a, n = m.search(s, time_limit=budget)
            return a, f"mcts rollouts={n}"
        return play_mcts
    ev = Evaluator(game, WEIGHT_SETS[args.weights] if args.weights else None)
    S = Searcher(game, ev, order=ORDERINGS[args.order], use_tt=not args.no_tt,
                 extensions=args.ext, check_every=1000)

    def play_ab(s, budget):
        r = S.search(s, time_limit=budget if args.depth is None else 1e9, max_depth=args.depth)
        v = "-" if r.value is None else f"{r.value:+.3f}"
        return r.move, f"derinlik={r.depth} değer={v} düğüm={r.nodes} tt={len(S.tt)}"
    return play_ab


def main():
    global ARGS
    ap = argparse.ArgumentParser(description="Connect-K ajanı")
    ap.add_argument("--R", type=int, default=MY_R)
    ap.add_argument("--C", type=int, default=MY_C)
    ap.add_argument("--K", type=int, default=MY_K)
    ap.add_argument("--V", type=int, default=MY_V)
    ap.add_argument("--seed", type=int, default=MY_D, help="engelli hücre çekimi için d")
    ap.add_argument("--time", type=float, default=0.8, help="hamle başına iç bütçe (s)")
    ap.add_argument("--first-time", type=float, default=0.55,
                    help="ilk komut için bütçe: hakem süreç açılır açılmaz MOVES gönderirse "
                         "Python'un açılışı (~0.1-0.2 s) da süreye sayılır")
    ap.add_argument("--algo", choices=["ab", "mcts", "random"], default="ab")
    ap.add_argument("--weights", choices=sorted(WEIGHT_SETS), default=None)
    ap.add_argument("--order", choices=sorted(ORDERINGS), default="d")
    ap.add_argument("--ext", type=int, default=4, help="ufuk uzatması (0 = kapalı)")
    ap.add_argument("--no-tt", action="store_true")
    ap.add_argument("--depth", type=int, default=None, help="sabit derinlik (süresiz; test için)")
    ap.add_argument("--rng", type=int, default=0, help="random/mcts için seed")
    ap.add_argument("--row-origin", choices=["bottom", "top"], default="bottom",
                    help="engelli hücre satır numarası alttan mı üstten mi sayılır")
    ap.add_argument("--quiet", action="store_true")
    ARGS = ap.parse_args()

    gc.disable()        # arama hiç döngüsel çöp üretmez; GC duraklaması süreyi aşmasın
    game = Game(ARGS.R, ARGS.C, ARGS.K, ARGS.V, d=ARGS.seed, row_origin=ARGS.row_origin)
    log("ajan hazır:", game.describe())
    player = build_player(game, ARGS)

    first = True
    for line in sys.stdin:
        t0 = time.perf_counter()
        parts = line.split()
        if not parts:
            continue
        cmd = parts[0].upper()
        if cmd == "QUIT":
            break
        if cmd != "MOVES":
            log("bilinmeyen komut:", line.strip())
            continue
        move, info = None, ""
        try:
            s = game.initial_state()
            for tok in parts[1:]:
                s = game.result(s, int(tok))
            acts = game.actions(s)
            if not acts:
                log("yasal hamle yok (oyun bitmiş ya da tahta dolu)")
                move = 0
            else:
                move = center_order(game, acts)[0]          # yedek hamle
                limit = min(ARGS.time, ARGS.first_time) if first else ARGS.time
                budget = max(0.05, limit - (time.perf_counter() - t0))
                a, info = player(s, budget)
                if a in acts:
                    move = a
                else:
                    log("arama yasa dışı hamle döndürdü:", a)
        except Exception as e:                                # asla çökme
            log("HATA:", repr(e))
            if move is None:
                try:
                    move = center_order(game, game.actions(s))[0]
                except Exception:
                    move = 0
        sys.stdout.write(f"{move}\n")
        sys.stdout.flush()
        log(f"hamle {move}  ({time.perf_counter() - t0:.3f} s)  {info}")


ARGS = None

if __name__ == "__main__":
    main()

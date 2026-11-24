"""Süreç içi (aynı Python süreci) maç oynatma yardımcıları."""
import random
import time

from game import MAX


def random_opening(game, plies, seed):
    rng = random.Random(seed)
    s, seq = game.initial_state(), []
    for _ in range(plies):
        a = rng.choice(game.actions(s))
        s2 = game.result(s, a)
        if game.is_terminal(s2):
            break
        s, seq = s2, seq + [a]
    return seq


def play_game(game, agent_first, agent_second, opening=()):
    """agent(game, s) -> sütun. Dönüş: dict(winner: 1/2/0, moves, times)."""
    s = game.play(list(opening))
    moves = list(opening)
    times = {1: [], 2: []}
    while not game.is_terminal(s):
        agent = agent_first if s.to_move == MAX else agent_second
        t = time.perf_counter()
        a = agent(game, s)
        times[s.to_move].append(time.perf_counter() - t)
        if a not in game.actions(s):
            raise RuntimeError(f"yasa dışı hamle {a}")
        s = game.result(s, a)
        moves.append(a)
    return {"winner": game.winner(s), "moves": moves, "times": times, "liner": s.liner}

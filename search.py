"""Arama algoritmaları.

Aşama 1: derinlik sınırlı minimax (max_value / min_value), düğüm sayacı.
Tüm değerler MAX gözüyledir (minimax yaklaşımı, negamax DEĞİL):
  terminal -> game.utility(s) in {-1, 0, +1};  derinlik sınırı -> evalf(game, s).
"""
from game import MAX

INF = float("inf")


class Stats:
    """Düğüm sayacı: her max_value/min_value çağrısında (ve kökte) bir artar."""
    __slots__ = ("nodes",)

    def __init__(self):
        self.nodes = 0


def eval_zero(game, s):
    """Aşama 1: henüz gerçek Eval yok."""
    return 0.0


def center_order(game, actions):
    """Beraberlik kuralı: merkeze yakın sütun önce, eşitse küçük indeks."""
    return sorted(actions, key=lambda a: (game.center_dist[a], a))


# ====================================================================== MINIMAX
def max_value(game, s, depth, evalf, stats):
    stats.nodes += 1
    if game.is_terminal(s):                 # 1) terminal kontrolü derinlikten ÖNCE
        return game.utility(s)
    if depth == 0:                          # 2) derinlik sınırı
        return evalf(game, s)
    v = -INF
    for a in game.actions(s):
        v = max(v, min_value(game, game.result(s, a), depth - 1, evalf, stats))
    return v


def min_value(game, s, depth, evalf, stats):
    stats.nodes += 1
    if game.is_terminal(s):
        return game.utility(s)
    if depth == 0:
        return evalf(game, s)
    v = INF
    for a in game.actions(s):
        v = min(v, max_value(game, game.result(s, a), depth - 1, evalf, stats))
    return v


def minimax_value(game, s, depth, evalf=eval_zero, stats=None):
    stats = stats or Stats()
    f = max_value if game.to_move(s) == MAX else min_value
    return f(game, s, depth, evalf, stats)


def minimax_decision(game, s, depth, evalf=eval_zero, stats=None, root_order=None):
    """Kökte her hamlenin çocuk değerini hesaplar, en iyisini seçer.
    Dönüş: (hamle, değer, düğüm_sayısı). Kök düğüm de sayılır (1 + C + C^2 ...).
    Eşit değerlilerde merkeze yakın olan seçilir (kesin, tekrarlanabilir)."""
    stats = stats or Stats()
    stats.nodes += 1
    acts = game.actions(s)
    if not acts:
        return None, game.utility(s), stats.nodes
    acts = root_order(game, acts) if root_order else center_order(game, acts)
    maximizing = game.to_move(s) == MAX
    child = min_value if maximizing else max_value
    best_a, best_v = None, None
    for a in acts:
        v = child(game, game.result(s, a), depth - 1, evalf, stats)
        if best_v is None or (v > best_v if maximizing else v < best_v):
            best_a, best_v = a, v
    return best_a, best_v, stats.nodes

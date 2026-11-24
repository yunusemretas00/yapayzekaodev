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


# ====================================================================== SIRALAMA
# Her sıralama fonksiyonu: order(game, s, actions) -> yeni liste.
def order_none(game, s, actions):
    """(a) sıralamasız: soldan sağa."""
    return actions


def order_center(game, s, actions):
    """(b) merkezden dışarı."""
    cd = game.center_dist
    return sorted(actions, key=lambda a: (cd[a], a))


def order_threat(game, s, actions):
    """(c) önce oyunu sırası gelen lehine bitiren hamle, sonra rakibin dizisini
    tamamlayacağı hücreyi kapatan (engelleme) hamle, sonra merkezden dışarı;
    sırası gelenin kendi aleyhine oyunu bitiren hamleler EN SONA.

    Standart: kendi dizini tamamlamak = kazanç (0), rakibin hücresini kapatmak = engel (1).
    Misère:   kendi dizini tamamlamak = kayıp (3, en sona); rakibin 'zehirli' hücresini
              doldurmak onu kurtarmaktır (2, normal hamlelerden sonra).
    """
    me = s.to_move
    opp = 3 - me
    misere = game.V == 2
    cd = game.center_dist
    keyed = []
    for a in actions:
        if game.completes_line(s, a, me):
            pri = 3 if misere else 0
        elif game.completes_line(s, a, opp):
            pri = 2 if misere else 1
        else:
            pri = 1.5 if misere else 2
        keyed.append((pri, cd[a], a))
    keyed.sort()
    return [k[2] for k in keyed]


ORDERINGS = {"a": order_none, "b": order_center, "c": order_threat}


# ====================================================================== ALFA-BETA
def ab_max_value(game, s, depth, alpha, beta, evalf, order, stats):
    stats.nodes += 1
    if game.is_terminal(s):
        return game.utility(s)
    if depth == 0:
        return evalf(game, s)
    v = -INF
    acts = game.actions(s)
    if order is not None:
        acts = order(game, s, acts)
    for a in acts:
        v = max(v, ab_min_value(game, game.result(s, a), depth - 1, alpha, beta, evalf, order, stats))
        if v >= beta:            # beta kesmesi
            return v
        alpha = max(alpha, v)
    return v


def ab_min_value(game, s, depth, alpha, beta, evalf, order, stats):
    stats.nodes += 1
    if game.is_terminal(s):
        return game.utility(s)
    if depth == 0:
        return evalf(game, s)
    v = INF
    acts = game.actions(s)
    if order is not None:
        acts = order(game, s, acts)
    for a in acts:
        v = min(v, ab_max_value(game, game.result(s, a), depth - 1, alpha, beta, evalf, order, stats))
        if v <= alpha:           # alfa kesmesi
            return v
        beta = min(beta, v)
    return v


def alphabeta_value(game, s, depth, evalf=eval_zero, order=None, stats=None):
    stats = stats or Stats()
    f = ab_max_value if game.to_move(s) == MAX else ab_min_value
    return f(game, s, depth, -INF, INF, evalf, order, stats)


def alphabeta_decision(game, s, depth, evalf=eval_zero, order=None, stats=None):
    """Kökte alpha = -inf, beta = +inf. Her çocuk aynı (alpha, beta) ile çağrılır
    ve kökte alpha (MIN sıradaysa beta) güncellenir.
    Dönüş: (hamle, değer, düğüm_sayısı)."""
    stats = stats or Stats()
    stats.nodes += 1
    acts = game.actions(s)
    if not acts:
        return None, game.utility(s), stats.nodes
    if order is not None:
        acts = order(game, s, acts)
    alpha, beta = -INF, INF
    best_a, best_v = None, None
    if game.to_move(s) == MAX:
        for a in acts:
            v = ab_min_value(game, game.result(s, a), depth - 1, alpha, beta, evalf, order, stats)
            if best_v is None or v > best_v:
                best_a, best_v = a, v
            alpha = max(alpha, v)
    else:
        for a in acts:
            v = ab_max_value(game, game.result(s, a), depth - 1, alpha, beta, evalf, order, stats)
            if best_v is None or v < best_v:
                best_a, best_v = a, v
            beta = min(beta, v)
    return best_a, best_v, stats.nodes

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
    m_me, m_op = (s.masks[0], s.masks[1]) if me == MAX else (s.masks[1], s.masks[0])
    if game.V == 2:
        P_OWN, P_OPP, P_NORMAL = 3, 2, 1.5
    else:
        P_OWN, P_OPP, P_NORMAL = 0, 1, 2
    C = game.C
    cw = game.cell_windows
    cd = game.center_dist
    heights = s.heights
    keyed = []
    for a in actions:
        i = heights[a] * C + a
        bit = 1 << i
        x, y = m_me | bit, m_op | bit
        pri = P_NORMAL
        for w in cw[i]:                 # = completes_line(me) / completes_line(opp)
            if x & w == w:
                pri = P_OWN
                break
            if y & w == w:
                pri = P_OPP
        keyed.append((pri, cd[a], a))
    keyed.sort()
    return [k[2] for k in keyed]


def order_threat_edge(game, s, actions):
    """(d) Misère-uyumlu (c): aynı öncelik sınıfları, ama Misère'de normal hamleler
    KENARDAN İÇE sıralanır. Gerekçe (Aşama 2 ölçümü): Misère'de merkez hücre daha çok
    pencereye girer -> kendi zehirli hücrelerini çoğaltır; iyi hamleler çoğunlukla
    kenarlardadır. Diğer varyantlarda (c) ile aynıdır."""
    if game.V != 2:
        return order_threat(game, s, actions)
    cd = game.center_dist
    me = s.to_move

    def key(a):
        if game.completes_line(s, a, me):          # intihar: en son
            return (3, 0, a)
        if game.completes_line(s, a, 3 - me):      # rakibin zehrini doldurmak
            return (2, 0, a)
        return (1, -cd[a], a)                      # normal: kenardan içe
    return sorted(actions, key=key)


def make_eval_order(evalf):
    """(e) Eval tabanlı sıralama: her çocuğun statik değeri (terminal ise faydası x2)
    sırası gelen oyuncunun gözüyle büyükten küçüğe. Pahalı (C kez result + Eval) ama
    en çok budamayı verir."""
    def order_eval(game, s, actions):
        sign = 1 if s.to_move == MAX else -1
        keyed = []
        for a in actions:
            c = game.result(s, a)
            v = 2 * game.utility(c) if (c.liner or c.n >= game.playable_cells) else evalf(game, c)
            keyed.append((-sign * v, game.center_dist[a], a))
        keyed.sort()
        return [k[2] for k in keyed]
    return order_eval


ORDERINGS = {"a": order_none, "b": order_center, "c": order_threat, "d": order_threat_edge}


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


# ====================================================================== AŞAMA 4
# İteratif derinleşme + zaman sınırı + yer değiştirme tablosu + ufuk uzatması
from time import perf_counter  # noqa: E402

EXACT, LOWER, UPPER = 0, 1, 2
FLAG_NAMES = {EXACT: "EXACT", LOWER: "LOWER", UPPER: "UPPER"}


class TimeUp(Exception):
    """Süre doldu: aramanın derinlerinden köke kadar fırlatılır."""


class SearchResult:
    def __init__(self, move, value, depth, nodes, sec, history, timed_out):
        self.move, self.value, self.depth = move, value, depth
        self.nodes, self.sec, self.history, self.timed_out = nodes, sec, history, timed_out

    def __repr__(self):
        return (f"SearchResult(move={self.move}, value={self.value}, depth={self.depth}, "
                f"nodes={self.nodes}, sec={self.sec:.3f}, timed_out={self.timed_out})")


class Searcher:
    """Zaman sınırlı α-β.

    order       : hamle sıralaması (varsayılan d); order_leaf: derinlik 1'de kullanılan sıralama
    use_tt      : Zobrist anahtarlı yer değiştirme tablosu (anahtar -> derinlik, değer, bayrak, en iyi hamle)
    extensions  : ufuk etkisi düzeltmesi; derinlik sınırına gelindiğinde konum 'sakin' değilse
                  (bir oyuncu oynanabilir bir hücrede dizi tamamlayabiliyorsa) aramayı 1 kat
                  uzatır; bir yol boyunca en fazla 'extensions' kez.
    check_every : süre kontrolü her bu kadar düğümde bir yapılır (perf_counter çağrısı pahalı).
    """

    def __init__(self, game, evalf, order=order_threat_edge, use_tt=True, extensions=0,
                 time_limit=0.8, check_every=1000, tt_max=1_500_000, order_leaf=None):
        self.game, self.evalf, self.order = game, evalf, order
        # derinlik 1 düğümlerinde (çocukları yaprak) kullanılacak, daha ucuz sıralama
        self.order_leaf = order_leaf or order
        self.use_tt, self.extensions = use_tt, extensions
        self.time_limit, self.check_every, self.tt_max = time_limit, check_every, tt_max
        self.tt = {}
        self.nodes = 0
        self.deadline = float("inf")
        self.next_check = check_every

    # ------------------------------------------------------------------ iç arama
    def _ab(self, s, depth, alpha, beta, ext):
        self.nodes += 1
        if self.nodes >= self.next_check:
            self.next_check = self.nodes + self.check_every
            if perf_counter() > self.deadline:
                raise TimeUp
        g = self.game
        if s.liner or s.n >= g.playable_cells:          # is_terminal (satır içi)
            return g.utility(s)
        if depth <= 0:
            if ext > 0 and not g.is_quiet(s):            # sakin değil: 1 kat uzat
                depth, ext = 1, ext - 1
            else:
                return self.evalf(g, s)

        tt_move = None
        if self.use_tt:
            e = self.tt.get(s.key)
            if e is not None:
                ed, ev, ef, em = e
                if ed >= depth:                          # yalnızca yeterince derin kayıt
                    if ef == EXACT:
                        return ev
                    if ef == LOWER:                      # gerçek değer >= ev
                        if ev >= beta:
                            return ev
                        if ev > alpha:
                            alpha = ev
                    else:                                # UPPER: gerçek değer <= ev
                        if ev <= alpha:
                            return ev
                        if ev < beta:
                            beta = ev
                tt_move = em
        a0, b0 = alpha, beta

        acts = (self.order if depth > 1 else self.order_leaf)(g, s, g.actions(s))
        if tt_move is not None and acts[0] != tt_move and tt_move in acts:  # (çakışmaya karşı)
            acts = [tt_move] + [a for a in acts if a != tt_move]
        best = acts[0]
        if s.to_move == MAX:
            v = -INF
            for a in acts:
                cv = self._ab(g.result(s, a), depth - 1, alpha, beta, ext)
                if cv > v:
                    v, best = cv, a
                if v >= beta:
                    break
                if v > alpha:
                    alpha = v
        else:
            v = INF
            for a in acts:
                cv = self._ab(g.result(s, a), depth - 1, alpha, beta, ext)
                if cv < v:
                    v, best = cv, a
                if v <= alpha:
                    break
                if v < beta:
                    beta = v

        if self.use_tt:
            # bayrak, gerçekten aranan pencereye (a0, b0) göre belirlenir
            flag = UPPER if v <= a0 else (LOWER if v >= b0 else EXACT)
            old = self.tt.get(s.key)
            if old is None or old[0] <= depth:           # derinlik öncelikli değiştirme
                self.tt[s.key] = (depth, v, flag, best)
        return v

    def _root(self, s, depth, first=None):
        g = self.game
        acts = self.order(g, s, g.actions(s))
        if first is not None and first in acts:          # önceki iterasyonun en iyisi önce
            acts = [first] + [a for a in acts if a != first]
        alpha, beta = -INF, INF
        best_a, best_v = None, None
        maximizing = s.to_move == MAX
        for a in acts:
            v = self._ab(g.result(s, a), depth - 1, alpha, beta, self.extensions)
            if maximizing:
                if best_v is None or v > best_v:
                    best_a, best_v = a, v
                alpha = max(alpha, v)
            else:
                if best_v is None or v < best_v:
                    best_a, best_v = a, v
                beta = min(beta, v)
        return best_a, best_v

    # ------------------------------------------------------------------ dış arayüz
    def search(self, s, time_limit=None, max_depth=None):
        """İteratif derinleşme: 1, 2, 3, ... Süre dolarsa yarım kalan derinlik atılır ve
        son TAMAMLANAN derinliğin hamlesi döndürülür."""
        g = self.game
        start = perf_counter()
        limit = self.time_limit if time_limit is None else time_limit
        self.deadline = start + limit
        self.nodes = 0
        self.next_check = self.check_every
        acts = g.actions(s)
        if not acts:
            return SearchResult(None, g.utility(s), 0, 0, 0.0, [], False)
        best_move, best_value, done_depth = center_order(g, acts)[0], None, 0
        if len(acts) == 1:
            return SearchResult(acts[0], None, 0, 0, perf_counter() - start, [], False)
        if len(self.tt) > self.tt_max:
            self.tt.clear()
        remaining = g.playable_cells - s.n
        max_depth = remaining if max_depth is None else min(max_depth, remaining)
        sign = 1 if s.to_move == MAX else -1
        history, timed_out = [], False
        for depth in range(1, max_depth + 1):
            try:
                m, v = self._root(s, depth, best_move if done_depth else None)
            except TimeUp:
                timed_out = True
                break
            history.append((depth, m, v, self.nodes, perf_counter() - start))
            if v * sign <= -1 and done_depth:
                # Kanıtlanmış kayıp: tüm hamleler kaybediyor. Bir önceki derinliğin
                # (kaybı henüz göremeyen, yani en uzun direnen) hamlesini koru.
                break
            best_move, best_value, done_depth = m, v, depth
            if v * sign >= 1:          # kanıtlanmış kazanç: ID en kısa kazancı ilk bulur
                break
        return SearchResult(best_move, best_value, done_depth, self.nodes,
                            perf_counter() - start, history, timed_out)

    def search_depth(self, s, depth):
        """Sabit derinlik (süresiz) - doğruluk testleri için. ID ile 1..depth."""
        return self.search(s, time_limit=1e9, max_depth=depth)

    def fixed_depth(self, s, depth):
        """Kısayolsuz sabit derinlik analizi (1..depth ID, süresiz): (hamle, değer).
        Terminal ya da hamlesiz durumda (None, utility)."""
        g = self.game
        if g.is_terminal(s):
            return None, g.utility(s)
        self.deadline = float("inf")
        self.nodes, self.next_check = 0, self.check_every
        depth = min(depth, g.playable_cells - s.n)
        m = None
        for d in range(1, depth + 1):
            m, v = self._root(s, d, m)
        return m, v

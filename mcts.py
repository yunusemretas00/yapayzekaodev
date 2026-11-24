"""Bonus: Monte Carlo ağaç araması (UCT), α-β ajanıyla karşılaştırma için.

* Seçim: UCB1 = W/N + c * sqrt(ln N_ebeveyn / N),  c = sqrt(2)
* Genişletme: denenmemiş bir hamle
* Simülasyon: "hafif akıllı" rastgele oyun: sırası gelen, oyunu kendi lehine bitiren
  hamle varsa onu oynar (Standart), kendi aleyhine bitirenden kaçınır (Misère: kendi
  dizisini tamamlamaz), yoksa rastgele.
* Geri yayılım: düğüme hamleyi yapan oyuncu kazandıysa 1, beraberlik 0.5.
* Karar: en çok ziyaret edilen çocuk.
"""
import math
import random
from time import perf_counter

from game import MISERE


class Node:
    __slots__ = ("state", "parent", "move", "children", "untried", "N", "W", "player")

    def __init__(self, game, state, parent=None, move=None):
        self.state, self.parent, self.move = state, parent, move
        self.children = []
        self.untried = game.actions(state)
        self.N, self.W = 0, 0.0
        self.player = 3 - state.to_move          # bu düğüme hamleyi yapan oyuncu


class MCTS:
    def __init__(self, game, time_limit=0.8, c=math.sqrt(2), seed=0):
        self.game, self.time_limit, self.c = game, time_limit, c
        self.rng = random.Random(seed)
        self.misere = game.V == MISERE
        self.rollouts = 0

    def _policy(self, s):
        g = self.game
        acts = g.actions(s)
        me = s.to_move
        good, safe = [], []
        for a in acts:
            if g.completes_line(s, a, me):
                if not self.misere:
                    good.append(a)
            else:
                safe.append(a)
        if good:
            return self.rng.choice(good)
        return self.rng.choice(safe or acts)

    def _rollout(self, s):
        g = self.game
        while not g.is_terminal(s):
            s = g.result(s, self._policy(s))
        return g.winner(s)

    def search(self, s, time_limit=None):
        g = self.game
        acts = g.actions(s)
        if len(acts) <= 1:
            return (acts[0] if acts else None), 0
        deadline = perf_counter() + (self.time_limit if time_limit is None else time_limit)
        root = Node(g, s)
        self.rollouts = 0
        logc = self.c
        while perf_counter() < deadline:
            node = root
            # seçim
            while not node.untried and node.children:
                lnN = math.log(node.N)
                node = max(node.children, key=lambda ch: ch.W / ch.N + logc * math.sqrt(lnN / ch.N))
            # genişletme
            if node.untried:
                a = node.untried.pop(self.rng.randrange(len(node.untried)))
                child = Node(g, g.result(node.state, a), node, a)
                node.children.append(child)
                node = child
            # simülasyon
            w = self._rollout(node.state)
            self.rollouts += 1
            # geri yayılım
            while node is not None:
                node.N += 1
                if w == 0:
                    node.W += 0.5
                elif w == node.player:
                    node.W += 1.0
                node = node.parent
        best = max(root.children, key=lambda ch: (ch.N, -g.center_dist[ch.move]))
        return best.move, self.rollouts

"""Aşama 2 testleri: α-β budaması ve hamle sıralaması.

Kontrol noktası 2 için: β kesme koşulundaki bir karakter değişirse
(ör. 'v >= beta' -> 'v > beta' ya da 'v <= beta') bu dosyadaki en az bir test kırılır:
  * '>' : değer aynı kalır ama düğüm sayısı artar -> test_beta_cut_on_equality,
          test_node_count_regression
  * '<=' ya da '<' : değer bozulur -> test_random_trees, test_matches_minimax_*
"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import MAX, MIN, my_game  # noqa: E402
from search import (alphabeta_decision, alphabeta_value, minimax_decision,  # noqa: E402
                    minimax_value, ORDERINGS, Stats, eval_zero)

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "experiments"))
from common import random_positions  # noqa: E402


class TreeGame:
    """Açık ağaç: iç düğüm = liste, yaprak = sayı (MAX gözüyle fayda)."""

    def __init__(self, tree, first=MAX):
        self.tree, self.first = tree, first

    def initial_state(self):
        return (self.tree, self.first)

    def to_move(self, s):
        return s[1]

    def actions(self, s):
        return list(range(len(s[0])))

    def result(self, s, a):
        return (s[0][a], MIN if s[1] == MAX else MAX)

    def is_terminal(self, s):
        return not isinstance(s[0], list)

    def utility(self, s):
        return s[0]


def random_tree(rng, depth, branching):
    if depth == 0:
        return rng.randint(-3, 3)           # küçük aralık -> bol eşitlik
    return [random_tree(rng, depth - 1, branching) for _ in range(rng.randint(1, branching))]


class TestAlphaBetaTrees(unittest.TestCase):
    def test_textbook_figure(self):
        """Russell & Norvig Şekil 5.5: kök değeri 3; ikinci MIN düğümü ilk yapraktan
        (2) sonra budanır -> ziyaret edilen yaprak 7, toplam düğüm 1 + 3 + 7 = 11."""
        g = TreeGame([[3, 12, 8], [2, 4, 6], [14, 5, 2]])
        a, v, nodes = alphabeta_decision(g, g.initial_state(), 10)
        self.assertEqual((a, v), (0, 3))
        self.assertEqual(nodes, 11)
        _, _, mm_nodes = minimax_decision(g, g.initial_state(), 10, root_order=lambda g_, x: x)
        self.assertEqual(mm_nodes, 13)

    def test_beta_cut_on_equality(self):
        """MIN kökü, iki MAX çocuğu. İlk çocuk 5 -> kökte beta = 5.
        İkinci çocukta ilk yaprak 5: v >= beta -> kes, 7 hiç görülmez."""
        g = TreeGame([[5, 1], [5, 7]], first=MIN)
        s = g.initial_state()
        st = Stats()
        self.assertEqual(alphabeta_value(g, s, 10, stats=st), 5)
        self.assertEqual(st.nodes, 1 + 1 + 2 + 1 + 1)   # 7'ye ait yaprak sayılmadı

    def test_alpha_cut_on_equality(self):
        g = TreeGame([[5, 9], [5, 1]], first=MAX)
        st = Stats()
        self.assertEqual(alphabeta_value(g, g.initial_state(), 10, stats=st), 5)
        self.assertEqual(st.nodes, 6)

    def test_random_trees(self):
        rng = random.Random(123)
        for i in range(400):
            t = random_tree(rng, rng.randint(1, 5), 4)
            if not isinstance(t, list):
                continue
            for first in (MAX, MIN):
                g = TreeGame(t, first)
                s = g.initial_state()
                st_mm, st_ab = Stats(), Stats()
                mm = minimax_value(g, s, 10, stats=st_mm)
                ab = alphabeta_value(g, s, 10, stats=st_ab)
                self.assertEqual(mm, ab, f"ağaç {i}: {t}")
                self.assertLessEqual(st_ab.nodes, st_mm.nodes)


class TestAlphaBetaGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = my_game()
        cls.positions = random_positions(cls.g, 50, seed=4242)

    def test_matches_minimax_50_positions(self):
        """50 rastgele konum, derinlik 4 (birim test hızlı olsun diye; deney
        betiği exp2 aynı karşılaştırmayı derinlik 6'da yapar)."""
        g = self.g
        for p in self.positions:
            s = g.play(p)
            mm_st = Stats()
            mm = minimax_value(g, s, 4, stats=mm_st)
            for name, order in ORDERINGS.items():
                st = Stats()
                a, v, _ = alphabeta_decision(g, s, 4, order=order, stats=st)
                self.assertEqual(v, mm, f"{p} sıralama {name}")
                # seçilen hamlenin GERÇEK değeri de kök değeri olmalı
                child = g.result(s, a)
                self.assertEqual(minimax_value(g, child, 3), mm)
                self.assertLessEqual(st.nodes, mm_st.nodes + 1)

    def test_ordering_win_first(self):
        from game import Game, STANDARD
        g = Game(5, 8, 4, STANDARD)
        s = g.play("0 0 1 1 2 2")
        self.assertEqual(ORDERINGS["c"](g, s, g.actions(s))[0], 3)       # kazanma önce
        g2 = my_game()
        s2 = g2.play("3 3 4 4 5 5")
        self.assertEqual(ORDERINGS["c"](g2, s2, g2.actions(s2))[-2:], [2, 6])  # Misère: intihar en son

    def test_node_count_regression(self):
        """Altın değer: kesme koşulu değişirse (değer aynı kalsa bile) düğüm sayısı değişir.
        Kod bilinçli olarak değiştirilirse bu sayıyı yeniden ölçüp güncelleyin."""
        g = self.g
        s = g.play("5 1 3 6 7 7 3 0 1 1 4")
        counts = []
        for name in "abc":
            counts.append(alphabeta_decision(g, s, 5, eval_zero, ORDERINGS[name])[2])
        self.assertEqual(counts, GOLDEN_COUNTS)


GOLDEN_COUNTS = [805, 804, 755]  # derinlik 5, eval_zero, sıralama a/b/c

if __name__ == "__main__":
    unittest.main()

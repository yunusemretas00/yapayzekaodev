"""Aşama 4 testleri: iteratif derinleşme, zaman sınırı, yer değiştirme tablosu."""
import os
import sys
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "experiments"))

from game import Game, STANDARD, MISERE, my_game  # noqa: E402
from evaluate import Evaluator  # noqa: E402
from search import Searcher, alphabeta_value, ORDERINGS  # noqa: E402
from common import random_positions  # noqa: E402


class TestZobrist(unittest.TestCase):
    def test_transposition_same_key(self):
        g = my_game()
        self.assertEqual(g.play("3 5 4").key, g.play("4 5 3").key)
        self.assertNotEqual(g.play("3 5 4").key, g.play("3 4 5").key)

    def test_side_to_move_in_key(self):
        g = my_game()
        # aynı taşlar farklı sırayla konamaz ama anahtar sıra bilgisini de içermeli:
        s = g.play("3")
        self.assertEqual(s.key, g.zobrist[1][3] ^ g.side_key)


class TestTTCorrectness(unittest.TestCase):
    def test_tt_value_equals_plain_alphabeta(self):
        """Tablo açıkken (ve kapalıyken) ID ile ulaşılan derinlik-D değeri,
        aynı sabit derinlikteki düz α-β değerine eşit olmalı."""
        g = my_game()
        ev = Evaluator(g)
        for p in random_positions(g, 30, seed=555):
            s = g.play(p)
            ref = alphabeta_value(g, s, 5, ev, ORDERINGS["c"])
            for tt in (True, False):
                r = Searcher(g, ev, use_tt=tt).search_depth(s, 5)
                self.assertEqual(r.history[-1][2], ref, f"tt={tt} {p}")

    def test_tt_standard_variant(self):
        g = Game(5, 7, 4, STANDARD)
        ev = Evaluator(g)
        for p in random_positions(g, 15, seed=556):
            s = g.play(p)
            ref = alphabeta_value(g, s, 5, ev, ORDERINGS["c"])
            self.assertEqual(Searcher(g, ev).search_depth(s, 5).history[-1][2], ref)


class TestTimeLimit(unittest.TestCase):
    def test_respects_limit(self):
        g = my_game()
        S = Searcher(g, Evaluator(g), time_limit=0.25)
        for p in random_positions(g, 5, seed=1):
            s = g.play(p)
            t = time.perf_counter()
            r = S.search(s)
            self.assertLess(time.perf_counter() - t, 0.32)
            self.assertIn(r.move, g.actions(s))
            self.assertGreaterEqual(r.depth, 1)

    def test_single_and_no_move(self):
        g = Game(2, 2, 4, MISERE)
        S = Searcher(g, Evaluator(g))
        s = g.play("0 0 1")
        self.assertEqual(S.search(s).move, 1)
        s = g.result(s, 1)
        self.assertIsNone(S.search(s).move)

    def test_shortest_win_and_avoids_poison(self):
        g = Game(5, 8, 4, STANDARD)
        r = Searcher(g, Evaluator(g)).search(g.play("0 0 1 1 2 2"), time_limit=0.5)
        self.assertEqual((r.move, r.value, r.depth), (3, 1, 1))
        g = my_game()
        r = Searcher(g, Evaluator(g), extensions=4).search(g.play("3 3 4 4 5 5"), time_limit=0.5)
        self.assertNotIn(r.move, (2, 6))


if __name__ == "__main__":
    unittest.main()

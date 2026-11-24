"""Aşama 1 testleri: minimax."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game, MAX, MIN, STANDARD, MISERE, my_game  # noqa: E402
from search import minimax_decision, minimax_value, Stats  # noqa: E402


class TestMinimax(unittest.TestCase):
    def test_depth2_node_count(self):
        g = my_game()
        _, _, nodes = minimax_decision(g, g.initial_state(), 2)
        self.assertEqual(nodes, 1 + g.C + g.C ** 2)

    def test_standard_win_in_one_and_block(self):
        g = Game(5, 8, 4, STANDARD)
        s = g.play("0 0 1 1 2 2")              # MAX: 3 koyarsa yatay 4
        self.assertEqual(minimax_decision(g, s, 2)[:2], (3, 1))
        s = g.play("0 1 0 1 0 1 7")            # MIN sırada: 1 ile dikey 4'lü
        self.assertEqual(minimax_decision(g, s, 1)[:2], (1, -1))
        s = g.play("0 1 0 1 7 1")              # MAX sırada; MIN dikey 3'lü -> 1'i engelle
        self.assertEqual(minimax_decision(g, s, 2)[0], 1)

    def test_misere_never_completes_own_line(self):
        g = my_game()
        s = g.play("3 3 4 4 5 5")              # MAX'in 2 ve 6 hamleleri kendini dizer
        for d in (1, 2, 3):
            a, v, _ = minimax_decision(g, s, d)
            self.assertNotIn(a, (2, 6))
            self.assertGreater(v, -1)
        s = g.play("3 3 4 4 5 5 0")            # aynı şey MIN için
        a, v, _ = minimax_decision(g, s, 2)
        self.assertNotIn(a, (2, 6))

    def test_misere_forced_loss_detected(self):
        """3x4 tahta, K=3 Misère, zugzwang:
            . O . .
            O X X .      MAX sırada; 0, 2, 3 hamlelerinin HEPSİ X'in 3'lüsünü
            O O X X      tamamlar -> MAX kaybetmeye zorlanır (değer -1)."""
        g = Game(3, 4, 3, MISERE)
        s = g.play("2 1 3 0 1 0 2 1")
        self.assertEqual(s.to_move, MAX)
        self.assertEqual(minimax_decision(g, s, 1)[1], -1)
        # bir önceki konumda MIN, MAX'i bu zugzwang'a sokan hamleyi bulmalı
        s = g.play("2 1 3 0 1 0 2")
        self.assertEqual(s.to_move, MIN)
        a, v, _ = minimax_decision(g, s, 2)
        self.assertEqual(v, -1)
        s2 = g.result(s, a)
        self.assertTrue(all(g.completes_line(s2, b, MAX) for b in g.actions(s2)))

    def test_deterministic(self):
        g = my_game()
        s = g.play("5 1 3 6 7 7 3 0 1 1 4")
        r1 = minimax_decision(g, s, 4)
        r2 = minimax_decision(g, s, 4)
        self.assertEqual(r1, r2)

    def test_value_matches_decision(self):
        g = my_game()
        s = g.play("3 3 4 4 5 5")
        _, v, _ = minimax_decision(g, s, 3)
        self.assertEqual(v, minimax_value(g, s, 3, stats=Stats()))


if __name__ == "__main__":
    unittest.main()

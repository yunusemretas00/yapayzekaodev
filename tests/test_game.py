"""Aşama 0 testleri: oyun modeli ve perft.

Çalıştırma:  python -m unittest discover -s tests -v
"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import (Game, MAX, MIN, perft, variant_from_d, my_game,  # noqa: E402
                  STANDARD, CYLINDER, MISERE, BLOCKED)


# ---------------------------------------------------------------- referans model
class NaiveGame:
    """Bilerek yavaş ve basit yazılmış ikinci bir model: 2B liste, her hamlede
    TÜM tahtayı tarar. Yalnızca perft çapraz kontrolü için."""

    def __init__(self, R, C, K, V, blocked=()):
        self.R, self.C, self.K, self.V = R, C, K, V
        self.blocked = set(blocked)

    def initial_state(self):
        g = [[0] * self.C for _ in range(self.R)]
        for (r, c) in self.blocked:
            g[r][c] = -1
        return (tuple(map(tuple, g)), MAX)

    def _landing(self, g, c):
        # yukarıdan düşen taş ilk dolu/engelli hücrenin üstünde durur
        r = self.R - 1
        if g[r][c] != 0:
            return None
        while r - 1 >= 0 and g[r - 1][c] == 0:
            r -= 1
        return r

    def _line(self, g, p):
        R, C, K = self.R, self.C, self.K
        for r in range(R):
            for c in range(C):
                for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                    ok = True
                    for k in range(K):
                        rr, cc = r + k * dr, c + k * dc
                        if self.V == CYLINDER:
                            cc %= C
                        if not (0 <= rr < R and 0 <= cc < C) or g[rr][cc] != p:
                            ok = False
                            break
                    if ok:
                        return True
        return False

    def is_terminal(self, s):
        g, _ = s
        if self._line(g, MAX) or self._line(g, MIN):
            return True
        return all(self._landing(g, c) is None for c in range(self.C))

    def actions(self, s):
        if self.is_terminal(s):
            return []
        return [c for c in range(self.C) if self._landing(s[0], c) is not None]

    def result(self, s, a):
        g, p = s
        r = self._landing(g, a)
        g2 = [list(row) for row in g]
        g2[r][a] = p
        return (tuple(map(tuple, g2)), MIN if p == MAX else MAX)


def random_position(game, rng, n_moves):
    s = game.initial_state()
    seq = []
    for _ in range(n_moves):
        acts = game.actions(s)
        if not acts:
            break
        a = rng.choice(acts)
        s2 = game.result(s, a)
        if game.is_terminal(s2):
            break
        s, seq = s2, seq + [a]
    return seq


class TestVariant(unittest.TestCase):
    def test_my_variant(self):
        # 232511042 -> d = 42 -> (R, C, K, V) = (5, 8, 4, 2)
        self.assertEqual(variant_from_d(42), (5, 8, 4, 2))
        self.assertEqual(variant_from_d(57), (5, 7, 4, 3))   # föydeki örnek


class TestPerft(unittest.TestCase):
    def test_empty_board_is_C_pow_n(self):
        g = my_game()
        s = g.initial_state()
        for n in range(1, 6):
            self.assertEqual(perft(g, s, n), g.C ** n, f"n={n}")
        # R = 5: ilk 5 hamlenin hepsi aynı sütuna giderse o sütun dolar ve 6. hamlede
        # C-1 seçenek kalır. Bu tam C dizide olur -> C^6 - C (föydeki "n <= 6 için
        # C^n" kuralı yalnızca R >= 6 için geçerli).
        self.assertEqual(perft(g, s, 6), g.C ** 6 - g.C)
        g6 = Game(6, 7, 4, MISERE)
        self.assertEqual(perft(g6, g6.initial_state(), 6), 7 ** 6)

    def test_perft_matches_naive_model_all_variants(self):
        rng = random.Random(7)
        for V in (STANDARD, CYLINDER, MISERE, BLOCKED):
            g = Game(5, 6, 4, V, d=42)
            ng = NaiveGame(5, 6, 4, V, g.blocked)
            for _ in range(6):
                seq = random_position(g, rng, rng.randint(8, 18))
                s, ns = g.play(seq), ng.initial_state()
                for a in seq:
                    ns = ng.result(ns, a)
                for n in (1, 2, 3):
                    self.assertEqual(perft(g, s, n), perft(ng, ns, n),
                                     f"V={V} seq={seq} n={n}")


class TestModel(unittest.TestCase):
    def test_full_column_leaves_actions(self):
        g = my_game()
        s = g.play("0 0 0 0")
        self.assertIn(0, g.actions(s))
        s = g.result(s, 0)          # 5. taş: sütun 0 doldu (R = 5)
        self.assertNotIn(0, g.actions(s))
        self.assertEqual(len(g.actions(s)), g.C - 1)
        with self.assertRaises(ValueError):
            g.result(s, 0)

    def test_result_is_immutable(self):
        g = my_game()
        s = g.play("3 4 3")
        before = (s.masks, s.heights, s.to_move, s.n)
        g.result(s, 5)
        g.result(s, 3)
        self.assertEqual(before, (s.masks, s.heights, s.to_move, s.n))

    def test_turn_alternates(self):
        g = my_game()
        s = g.initial_state()
        self.assertEqual(s.to_move, MAX)
        s = g.result(s, 2)
        self.assertEqual(s.to_move, MIN)

    def _check_win(self, g, seq, expected_utility):
        s = g.play(seq[:-1])
        self.assertFalse(g.is_terminal(s), "son hamleden önce terminal olmamalı")
        s = g.result(s, seq[-1])
        self.assertTrue(g.is_terminal(s))
        self.assertEqual(g.utility(s), expected_utility)

    def test_four_line_shapes_standard(self):
        g = Game(5, 8, 4, STANDARD)
        self._check_win(g, [0, 0, 1, 1, 2, 2, 3], +1)                      # yatay
        self._check_win(g, [0, 1, 0, 1, 0, 1, 0], +1)                      # dikey
        self._check_win(g, [0, 1, 1, 2, 2, 3, 2, 3, 3, 7, 3], +1)          # çapraz /
        self._check_win(g, [7, 6, 6, 5, 5, 4, 5, 4, 4, 0, 4], +1)          # çapraz \
        self._check_win(g, [0, 1, 0, 1, 7, 1, 7, 1], -1)                   # MIN dikey

    def test_misere_liner_loses(self):
        """Varyantıma özgü test 1: Misère'de diziyi yapan kaybeder."""
        g = my_game()
        self.assertEqual(g.V, MISERE)
        self._check_win(g, [0, 0, 1, 1, 2, 2, 3], -1)       # MAX dizdi -> MAX kaybeder
        self._check_win(g, [0, 1, 0, 1, 7, 1, 7, 1], +1)    # MIN dizdi -> MAX kazanır
        self._check_win(g, [0, 1, 1, 2, 2, 3, 2, 3, 3, 7, 3], -1)

    def test_misere_draw_when_full(self):
        """Varyantıma özgü test 2: kimse dizmeden tahta dolarsa beraberlik.
        K=4'lük dizinin hiç sığmadığı 3x3 tahtada tüm oyun beraberedir."""
        g = Game(3, 3, 4, MISERE)
        s = g.play("0 1 2 0 1 2 0 1 2")
        self.assertTrue(g.is_terminal(s))
        self.assertEqual(g.utility(s), 0)
        self.assertEqual(g.actions(s), [])

    def test_cylinder_wraps(self):
        g = Game(5, 8, 4, CYLINDER)
        seq = [6, 6, 7, 7, 0, 0, 1]          # 6-7-0-1 kenardan geçen yatay
        self._check_win(g, seq, +1)
        g0 = Game(5, 8, 4, STANDARD)
        self.assertFalse(g0.is_terminal(g0.play(seq)))

    def test_blocked_cells(self):
        g = Game(5, 8, 4, BLOCKED, blocked=[(2, 3), (4, 5)])
        s = g.initial_state()
        self.assertNotIn(5, g.actions(s))            # tepe hücresi engelli: sütun baştan dolu
        s = g.result(s, 3)
        self.assertEqual(g.cell(s, 3, 3), MAX)       # taş engelin üstünde durur
        self.assertEqual(g.cell(s, 0, 3), 0)         # engelin altı boş ve ulaşılamaz
        s = g.result(s, 3)
        self.assertNotIn(3, g.actions(s))            # 2 hücrede sütun doldu
        self.assertEqual(g.playable_cells, 6 * 5 + 2 + 0)  # 6 normal sütun + 2 + 0
        # föydeki çekim: aynı d her zaman aynı iki hücreyi verir
        self.assertEqual(Game(5, 7, 4, BLOCKED, d=57).blocked,
                         Game(5, 7, 4, BLOCKED, d=57).blocked)
        self.assertEqual(len(Game(5, 7, 4, BLOCKED, d=57).blocked), 2)


if __name__ == "__main__":
    unittest.main()

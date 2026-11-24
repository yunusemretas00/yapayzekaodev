"""Aşama 3 testleri: değerlendirme fonksiyonu."""
import os
import sys
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "experiments"))

from game import Game, STANDARD, CYLINDER, my_game  # noqa: E402
from evaluate import Evaluator, WEIGHT_SETS  # noqa: E402
from search import alphabeta_decision, ORDERINGS  # noqa: E402
from common import random_positions  # noqa: E402


class TestEval(unittest.TestCase):
    def test_hand_computed_features(self):
        g = my_game()
        e = Evaluator(g, WEIGHT_SETS["A"])
        s = g.play("3 3 4 4 5 5")
        # X: 3,4,5 (satır 0) | O: 3,4,5 (satır 1)
        # f1: X'in 3'lü pencereleri {2-5}, {3-6}; f2: {1-4}, {4-7}; O için aynısı
        # f6: X için 2 ve 6 zehirli -> güvenli 6; O'nun zehirli hücreleri henüz oynanamaz -> 8
        self.assertEqual(e.features(s), (2, 2, 2, 2, 0, -2))

    def test_range(self):
        g = my_game()
        for name, w in WEIGHT_SETS.items():
            e = Evaluator(g, w)
            for p in random_positions(g, 40, seed=9, max_moves=30):
                v = e(g, g.play(p))
                self.assertTrue(-1 < v < 1, f"{name}: {v}")

    def test_mirror_symmetry(self):
        """Standart ve Misère'de sol-sağ ayna konum aynı Eval'i verir."""
        for g in (my_game(), Game(5, 8, 4, STANDARD)):
            e = Evaluator(g)
            for p in random_positions(g, 40, seed=11, max_moves=25):
                s = g.play(p)
                self.assertAlmostEqual(e(g, s), e(g, g.mirror(s)), places=12)

    def test_cylinder_has_no_edges(self):
        """Silindirde tüm sütunlar eşdeğerdir: tahtayı 1 sütun döndürmek Eval'i değiştirmez
        (merkez özniteliği hariç; ağırlığı 0 alınır)."""
        g = Game(5, 8, 4, CYLINDER)
        w = dict(WEIGHT_SETS["S"], f5=0.0)
        e = Evaluator(g, w)
        p = [3, 4, 4, 5, 7, 7, 0]
        rot = [(a + 1) % 8 for a in p]
        self.assertAlmostEqual(e(g, g.play(p)), e(g, g.play(rot)), places=12)

    def test_eval_never_called_on_terminal(self):
        g = my_game()
        e = Evaluator(g)

        def guarded(game, s):
            assert not game.is_terminal(s), "Eval terminal durumda çağrıldı"
            return e(game, s)
        for p in random_positions(g, 10, seed=3, min_moves=12, max_moves=24):
            alphabeta_decision(g, g.play(p), 3, guarded, ORDERINGS["c"])

    def test_fast(self):
        g = my_game()
        e = Evaluator(g)
        s = g.play("5 1 4 4 7 2 4 0 5 5 7 6 1 6 7 1 6 7 6 4 6")
        n = 5000
        t = time.perf_counter()
        for _ in range(n):
            e(g, s)
        self.assertLess((time.perf_counter() - t) / n, 200e-6)


if __name__ == "__main__":
    unittest.main()

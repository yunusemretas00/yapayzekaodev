"""Aşama 5 testleri: komut satırı protokolü (agent.py alt süreç olarak çalıştırılır)."""
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from game import Game  # noqa: E402

AGENT = os.path.join(ROOT, "agent.py")


def run_agent(lines, *extra):
    p = subprocess.run([sys.executable, AGENT, "--quiet", "--time", "0.2", *extra],
                       input="\n".join(lines) + "\n", capture_output=True, text=True, timeout=60)
    return p.returncode, [x for x in p.stdout.splitlines() if x.strip()]


class TestAgentProtocol(unittest.TestCase):
    def test_moves_and_quit(self):
        code, out = run_agent(["MOVES", "MOVES 3 3 4 4 5 5", "QUIT", "MOVES 1"])
        self.assertEqual(code, 0)
        self.assertEqual(len(out), 2)                  # QUIT'ten sonrası okunmaz
        self.assertNotIn(int(out[1]), (2, 6))          # Misère: kendi 4'lüsünü tamamlamaz

    def test_only_legal_column(self):
        # 3x3 tahtada K=4 dizisi hiç oluşamaz: 0 ve 2 dolunca tek yasal sütun 1
        g = Game(3, 3, 4, 2)
        seq = [0, 0, 0, 2, 2, 2]
        s = g.play(seq)
        self.assertEqual(g.actions(s), [1])
        code, out = run_agent(["MOVES " + " ".join(map(str, seq)), "QUIT"],
                              "--R", "3", "--C", "3", "--K", "4", "--V", "2")
        self.assertEqual(out, ["1"])

    def test_no_legal_move_does_not_crash(self):
        g = Game(2, 2, 4, 2)
        code, out = run_agent(["MOVES 0 0 1 1", "QUIT"], "--R", "2", "--C", "2", "--K", "4", "--V", "2")
        self.assertEqual(code, 0)
        self.assertEqual(len(out), 1)

    def test_unexpected_variants(self):
        """K = 5, R = 7, C = 8, her V değeri."""
        for V in range(4):
            g = Game(7, 8, 5, V, d=7)
            code, out = run_agent(["MOVES", "MOVES 0 7 1", "QUIT"],
                                  "--R", "7", "--C", "8", "--K", "5", "--V", str(V), "--seed", "7")
            self.assertEqual(code, 0, f"V={V}")
            self.assertEqual(len(out), 2, f"V={V}")
            self.assertIn(int(out[0]), g.actions(g.initial_state()))
            self.assertIn(int(out[1]), g.actions(g.play("0 7 1")))


if __name__ == "__main__":
    unittest.main()

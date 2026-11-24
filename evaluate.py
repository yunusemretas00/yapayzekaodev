"""Aşama 3: değerlendirme fonksiyonu  Eval(s) = 0.999 * tanh( (Σ wᵢ fᵢ(s)) / ölçek ).

Tüm öznitelikler MAX gözüyledir (minimax ile tutarlı). Pencereler (K hücrelik her
yatay/dikey/çapraz dizi; silindirde sarmalı, engelli hücre içerenler hariç) Game
nesnesinde BİR KEZ hesaplanır; Eval her çağrıda yalnızca bu listeyi dolaşır.

Öznitelikler (bir pencerede iki tarafın da taşı varsa pencere kimseye değmez):
  f1  MAX'in K-1 taşı + 1 boş olan pencere sayısı   ("acil tehdit"; Misère'de zehir)
  f2  MAX'in K-2 taşı + 2 boş olan pencere sayısı
  f3  MIN'in K-1 taşı + 1 boş olan pencere sayısı
  f4  MIN'in K-2 taşı + 2 boş olan pencere sayısı
  f5  merkez sütun kontrolü: merkez sütunlardaki MAX taşı - MIN taşı
  f6  (Misère'e özgü) "dizmeye zorlanmayacağım" göstergesi:
      MAX için güvenli oynanabilir sütun sayısı - MIN için güvenli oynanabilir sütun sayısı.
      Bir sütun p için güvenlidir: sütun dolu değil ve taşın düşeceği hücre p'nin
      kendi K'lık dizisini TAMAMLAMIYOR. Misère'de oyunu, güvenli hamlesi önce
      biten oyuncu kaybeder (zugzwang); f6 bunu doğrudan ölçer.

Misère'de işaretler tersine döner: K-1'lik kendi pencerem artık tehdit değil,
kaçınmam gereken "zehirli hücre"dir. Hangi işaretin doğru olduğu exp3 ile ölçüldü.
"""
import math

from game import MISERE, CYLINDER

FEATURES = ("f1", "f2", "f3", "f4", "f5", "f6")

# Standart / silindir / engelli için klasik ağırlıklar
W_STANDARD = {"f1": 1.0, "f2": 0.25, "f3": -1.0, "f4": -0.25, "f5": 0.15, "f6": 0.0}

# Misère için üç aday (Aşama 3 ağırlık ayarı; bkz. experiments/exp3_weights.py)
W_MISERE_A = {"f1": -1.0, "f2": -0.25, "f3": 1.0, "f4": 0.25, "f5": 0.0, "f6": 0.5}   # ters-simetrik (varsayılan tahmin)
W_MISERE_B = {"f1": 1.0, "f2": 0.25, "f3": -1.0, "f4": -0.25, "f5": 0.15, "f6": 0.0}  # naif: standart işaretler
W_MISERE_C = {"f1": -0.5, "f2": 0.0, "f3": 0.5, "f4": 0.0, "f5": 0.0, "f6": 1.5}      # güvenli hamle ağırlıklı

WEIGHT_SETS = {"A": W_MISERE_A, "B": W_MISERE_B, "C": W_MISERE_C, "S": W_STANDARD}
DEFAULT_MISERE = "A"


def default_weights(game):
    if game.V == MISERE:
        return dict(WEIGHT_SETS[DEFAULT_MISERE])
    w = dict(W_STANDARD)
    if game.V == CYLINDER:
        w["f5"] = 0.0          # silindirde her sütun eşdeğer: "merkez" yok
    return w


class Evaluator:
    """evalf(game, s) olarak çağrılır."""

    def __init__(self, game, weights=None, scale=6.0):
        self.game = game
        self.w = dict(weights) if weights is not None else default_weights(game)
        self.scale = scale
        self.windows = game.windows
        self.K = game.K
        R, C = game.R, game.C
        self.R, self.C = R, C
        # oynanabilir hücre tablosu: land[c][h] = (h, c) hücresinin biti
        self.land = [[1 << (h * C + c) for h in range(R)] for c in range(C)]
        self.center_mask = 0
        for c in range(C):
            if game.center_dist[c] <= 1.0:
                for r in range(R):
                    self.center_mask |= 1 << (r * C + c)
        self.wv = [self.w[f] for f in FEATURES]

    def features(self, s):
        m1, m2 = s.masks
        occ = m1 | m2
        K1, K2 = self.K - 1, self.K - 2
        a1 = b1 = a2 = b2 = 0
        p1 = p2 = 0                     # zehirli/kazandıran boş hücre maskeleri
        for w in self.windows:
            x = m1 & w
            y = m2 & w
            if x:
                if y:
                    continue
                n = x.bit_count()
                if n == K1:
                    a1 += 1
                    p1 |= w & ~occ
                elif n == K2:
                    b1 += 1
            elif y:
                n = y.bit_count()
                if n == K1:
                    a2 += 1
                    p2 |= w & ~occ
                elif n == K2:
                    b2 += 1
        cm = self.center_mask
        f5 = (m1 & cm).bit_count() - (m2 & cm).bit_count()
        play = 0
        R = self.R
        for c, h in enumerate(s.heights):
            if h < R:
                play |= self.land[c][h]
        f6 = (play & ~p1).bit_count() - (play & ~p2).bit_count()
        return (a1, b1, a2, b2, f5, f6)

    def raw(self, s):
        return sum(w * f for w, f in zip(self.wv, self.features(s)))

    def __call__(self, game, s):
        w1, w2, w3, w4, w5, w6 = self.wv
        f1, f2, f3, f4, f5, f6 = self.features(s)
        raw = w1 * f1 + w2 * f2 + w3 * f3 + w4 * f4 + w5 * f5 + w6 * f6
        # [-1, +1] aralığına sıkıştır; 0.999 çarpanı gerçek kazanç/kayıptan (±1)
        # her zaman kesin olarak küçük kalmayı garanti eder.
        return 0.999 * math.tanh(raw / self.scale)

    def explain(self, s):
        f = self.features(s)
        lines = [f"{n} = {v:3d}   x w = {self.w[n]:+.2f}  -> {self.w[n] * v:+.3f}" for n, v in zip(FEATURES, f)]
        raw = self.raw(s)
        lines.append(f"ham toplam = {raw:+.3f};  Eval = 0.999*tanh({raw:+.3f}/{self.scale}) = "
                     f"{0.999 * math.tanh(raw / self.scale):+.4f}")
        return "\n".join(lines)


if __name__ == "__main__":
    # Kontrol noktası 3: python evaluate.py "3 3 4 4 5 5"
    import sys
    from game import my_game
    g = my_game()
    s = g.play(sys.argv[1] if len(sys.argv) > 1 else "")
    print(g.describe())
    print(g.render(s))
    print(Evaluator(g).explain(s))

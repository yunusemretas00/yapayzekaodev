"""Connect-K oyun modeli (Aşama 0).

Durum gösterimi (Seçenek B'nin bit karşılığı):
  * Hücre indeksi  i = satır * C + sütun ; satır 0 = EN ALT satır.
  * Her oyuncunun taşları bir tam sayının bitleri (masks[0] = MAX, masks[1] = MIN).
  * heights[c] = c sütununda bir sonraki taşın düşeceği satır (R ise sütun dolu).
  * Durum değişmez (immutable): result() her zaman YENİ bir State döndürür.

Kazanma kontrolü "pencere" listesiyle yapılır: tahtadaki K uzunluğundaki her
yatay/dikey/çapraz dizi bir bit maskesi olarak bir kez hesaplanır (silindirde
sütunlar mod C ile sarılır, engelli hücre içeren pencereler hiç üretilmez).
Son konan taşın içinde bulunduğu pencerelerden biri tamamen o oyuncunun ise
dizi oluşmuştur. Böylece dört varyasyon aynı kodla çalışır.
"""
import random

MAX, MIN = 1, 2
STANDARD, CYLINDER, MISERE, BLOCKED = 0, 1, 2, 3
VARIANT_NAMES = {0: "Standart", 1: "Silindir", 2: "Misère", 3: "Engelli"}
DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))  # (dsatır, dsütun)


def variant_from_d(d):
    """Öğrenci numarasının son iki hanesinden (R, C, K, V)."""
    R = 5 + (d % 3)
    C = 6 + ((d // 3) % 3)
    K = 4 + ((d // 9) % 2)
    V = (d // 18) % 4
    return R, C, K, V


def other(p):
    return MIN if p == MAX else MAX


class State:
    """Değişmez oyun durumu. Alanlar yalnızca okunur kabul edilir."""
    __slots__ = ("masks", "heights", "to_move", "n", "last", "liner", "key")

    def __init__(self, masks, heights, to_move, n, last, liner, key):
        self.masks = masks        # (MAX maskesi, MIN maskesi)
        self.heights = heights    # tuple, sütun başına sıradaki boş satır
        self.to_move = to_move    # MAX ya da MIN: sıra kimde
        self.n = n                # şu ana kadar oynanan hamle sayısı
        self.last = last          # son konan taşın hücre indeksi (yoksa -1)
        self.liner = liner        # K'lık diziyi yapan oyuncu (yoksa 0)
        self.key = key            # Zobrist anahtarı (Aşama 4)

    def __repr__(self):
        return f"State(n={self.n}, to_move={self.to_move}, liner={self.liner})"


class Game:
    def __init__(self, R, C, K, V, d=0, blocked=None, row_origin="bottom",
                 zobrist_seed=20241142):
        if V not in (0, 1, 2, 3):
            raise ValueError("V 0..3 olmalı")
        self.R, self.C, self.K, self.V, self.d = R, C, K, V, d
        self.N = R * C
        # --- engelli hücreler (V = 3) ---
        if blocked is None:
            blocked = self.draw_blocked(R, C, d, row_origin) if V == BLOCKED else []
        self.blocked = sorted(set(blocked))
        self.blocked_mask = 0
        for (r, c) in self.blocked:
            self.blocked_mask |= 1 << self.idx(r, c)
        # Taşlar engelin üstünde durur: sütunun başlangıç yüksekliği, o sütundaki
        # en yüksek engelin bir üstü. Altındaki hücrelere hiç ulaşılamaz.
        h0 = [0] * C
        for (r, c) in self.blocked:
            h0[c] = max(h0[c], r + 1)
        self.initial_heights = tuple(h0)
        self.playable_cells = sum(R - h for h in h0)
        # --- pencereler ---
        self.windows = self._build_windows()
        self.cell_windows = [[] for _ in range(self.N)]
        for w in self.windows:
            m = w
            while m:
                low = m & -m
                self.cell_windows[low.bit_length() - 1].append(w)
                m ^= low
        # --- Zobrist (Aşama 4) ---
        rng = random.Random(zobrist_seed)
        self.zobrist = (None,
                        [rng.getrandbits(64) for _ in range(self.N)],
                        [rng.getrandbits(64) for _ in range(self.N)])
        self.side_key = rng.getrandbits(64)
        # sütun sıralaması için merkez uzaklığı (beraberlik kuralı)
        mid = (C - 1) / 2
        self.center_dist = [abs(c - mid) for c in range(C)]

    # ------------------------------------------------------------------ yardımcılar
    @staticmethod
    def draw_blocked(R, C, d, row_origin="bottom"):
        """Föydeki kural: rng = random.Random(d); iki kez (satır, sütun) çek,
        aynı hücre çıkarsa yeniden çek. row_origin='top' ise çekilen satır
        üstten sayılır (satır 0 = en üst) ve iç gösterime çevrilir."""
        rng = random.Random(d)
        cells = []
        while len(cells) < 2:
            r = rng.randrange(R)
            c = rng.randrange(C)
            if row_origin == "top":
                r = R - 1 - r
            if (r, c) not in cells:
                cells.append((r, c))
        return cells

    def idx(self, r, c):
        return r * self.C + c

    def _build_windows(self):
        R, C, K = self.R, self.C, self.K
        cyl = self.V == CYLINDER
        seen, out = set(), []
        for r in range(R):
            for c in range(C):
                for dr, dc in DIRECTIONS:
                    m, ok = 0, True
                    for k in range(K):
                        rr, cc = r + k * dr, c + k * dc
                        if not (0 <= rr < R):
                            ok = False
                            break
                        if cyl:
                            cc %= C          # (sütun ± 1) mod C, negatif indeks yok
                        elif not (0 <= cc < C):
                            ok = False
                            break
                        bit = 1 << (rr * C + cc)
                        if bit & self.blocked_mask or bit & m:
                            ok = False       # engelli hücre diziye dahil olamaz
                            break
                        m |= bit
                    if ok and m not in seen:
                        seen.add(m)
                        out.append(m)
        return out

    # ------------------------------------------------------------------ oyun arayüzü
    def initial_state(self):
        return State((0, 0), self.initial_heights, MAX, 0, -1, 0, 0)

    def to_move(self, s):
        return s.to_move

    def actions(self, s):
        """Yasal sütunlar (soldan sağa). Terminal durumda boş liste."""
        if s.liner:
            return []
        R = self.R
        return [c for c, h in enumerate(s.heights) if h < R]

    def result(self, s, a):
        h = s.heights[a]
        if h >= self.R or s.liner:
            raise ValueError(f"yasa dışı hamle: {a}")
        i = h * self.C + a
        bit = 1 << i
        p = s.to_move
        if p == MAX:
            m = s.masks[0] | bit
            masks = (m, s.masks[1])
        else:
            m = s.masks[1] | bit
            masks = (s.masks[0], m)
        heights = s.heights[:a] + (h + 1,) + s.heights[a + 1:]
        # Taş KONDUKTAN sonra, yalnızca bu taşı içeren pencereler kontrol edilir.
        liner = 0
        for w in self.cell_windows[i]:
            if m & w == w:
                liner = p
                break
        key = s.key ^ self.zobrist[p][i] ^ self.side_key
        return State(masks, heights, MIN if p == MAX else MAX, s.n + 1, i, liner, key)

    def is_full(self, s):
        return s.n >= self.playable_cells

    def is_terminal(self, s):
        return s.liner != 0 or s.n >= self.playable_cells

    def winner(self, s):
        """Kazanan oyuncu (beraberlik/bitmemiş: 0). Misère'de diziyi yapan kaybeder."""
        if not s.liner:
            return 0
        return other(s.liner) if self.V == MISERE else s.liner

    def utility(self, s):
        """Her zaman MAX gözüyle: +1 / 0 / -1."""
        w = self.winner(s)
        return 1 if w == MAX else (-1 if w == MIN else 0)

    # ------------------------------------------------------------------ araçlar
    def completes_line(self, s, col, player):
        """col sütununa player taş koysa K'lık dizi oluşur mu?"""
        h = s.heights[col]
        if h >= self.R:
            return False
        i = h * self.C + col
        m = s.masks[player - 1] | (1 << i)
        for w in self.cell_windows[i]:
            if m & w == w:
                return True
        return False

    def is_quiet(self, s):
        """Hiçbir oyuncunun şu an oynanabilir bir hücrede diziyi tamamlayamadığı
        konum 'sakin'dir (Aşama 4 ufuk etkisi düzeltmesi)."""
        R, C = self.R, self.C
        m1, m2 = s.masks
        cw = self.cell_windows
        for c, h in enumerate(s.heights):
            if h < R:
                i = h * C + c
                bit = 1 << i
                a, b = m1 | bit, m2 | bit
                for w in cw[i]:
                    if a & w == w or b & w == w:
                        return False
        return True

    def cell(self, s, r, c):
        bit = 1 << (r * self.C + c)
        if s.masks[0] & bit:
            return MAX
        if s.masks[1] & bit:
            return MIN
        if self.blocked_mask & bit:
            return -1
        return 0

    def play(self, moves, s=None):
        """Hamle dizisini ('3 3 4 4' ya da liste) uygula."""
        if isinstance(moves, str):
            moves = [int(x) for x in moves.split()]
        s = self.initial_state() if s is None else s
        for a in moves:
            s = self.result(s, a)
        return s

    def mirror(self, s):
        """Sol-sağ ayna görüntüsü (test için)."""
        C = self.C
        moves_masks = []
        for m in s.masks:
            mm = 0
            for i in range(self.N):
                if m >> i & 1:
                    r, c = divmod(i, C)
                    mm |= 1 << (r * C + (C - 1 - c))
            moves_masks.append(mm)
        heights = tuple(reversed(s.heights))
        return State(tuple(moves_masks), heights, s.to_move, s.n, -1, s.liner, 0)

    def render(self, s):
        sym = {MAX: "X", MIN: "O", 0: ".", -1: "#"}
        rows = []
        for r in range(self.R - 1, -1, -1):
            rows.append(" ".join(sym[self.cell(s, r, c)] for c in range(self.C)))
        rows.append(" ".join(str(c % 10) for c in range(self.C)))
        return "\n".join(rows)

    def describe(self):
        return (f"R={self.R}, C={self.C}, K={self.K}, V={self.V} "
                f"({VARIANT_NAMES[self.V]}), d={self.d}, engelli={self.blocked}")


def perft(game, s, n):
    """Tam derinlik n'deki yaprak sayısı (föydeki tanım)."""
    if n == 0 or game.is_terminal(s):
        return 1
    return sum(perft(game, game.result(s, a), n - 1) for a in game.actions(s))


# Benim varyantım: öğrenci no 232511042 -> d = 42
MY_D = 42
MY_R, MY_C, MY_K, MY_V = variant_from_d(MY_D)


def my_game():
    return Game(MY_R, MY_C, MY_K, MY_V, d=MY_D)

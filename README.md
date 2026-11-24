# Connect-K Arena — öğrenci no 232511042 (d = 42)

**Varyant: (R, C, K, V, d) = (5, 8, 4, 2, 42) — Misère**: K taşı dizen oyuncu kaybeder.

## Dosyalar

| dosya | içerik |
|---|---|
| `game.py` | Aşama 0: oyun modeli (değişmez durum, 4 varyasyon), `perft` |
| `search.py` | Aşama 1-4: minimax, α-β, sıralamalar (a-e), `Searcher` (ID + zaman + Zobrist tablosu + ufuk uzatması) |
| `evaluate.py` | Aşama 3: pencere tabanlı Eval (6 öznitelik), ağırlık vektörleri A/B/C/S |
| `agent.py` | Aşama 5: komut satırı ajanı (MOVES / QUIT protokolü) |
| `mcts.py` | Bonus: UCT Monte Carlo ağaç araması |
| `arena.py` | Yerel hakem: iki ajan sürecini protokolle oynatır, süreyi ölçer |
| `tests/` | 42 birim testi (`python -m unittest discover -s tests -v`) |
| `experiments/` | Rapordaki her sayıyı üreten betikler |
| `data/` | Ölçüm konumları (öğretmenin konumları buraya yazılabilir) |
| `results/`, `figures/` | Ölçüm çıktıları (md + json) ve grafikler |
| `rapor.md` | Rapor |
| `PROMPTLAR.md` | Yapay zekâ kullanım tutanağı |

## Çalıştırma

```bash
python -m unittest discover -s tests -v          # tüm testler (~15 s)

python agent.py --R 5 --C 8 --K 4 --V 2 --seed 42  # turnuva ajanı (stdin: MOVES 3 3 4 / QUIT)
python evaluate.py "3 3 4 4 5 5"                 # bir konumda Eval ve öznitelikler (kontrol noktası 3)
python arena.py --a "python agent.py" --b "python agent.py --algo mcts" --games 4
```

## Ölçümleri yeniden üretme (sırasıyla)

```bash
python experiments/exp0_perft.py      [--pos "3 3 4 4 5 5" --nmax 4]   # Aşama 0, kontrol noktası 0
python experiments/exp1_minimax.py    [--pos "..."]                    # Aşama 1
python experiments/exp2_alphabeta.py  --eval zero ; python experiments/exp2_alphabeta.py --eval full   # Aşama 2
python experiments/exp3_weights.py                                    # Aşama 3 ağırlık ayarı (paralel)
python experiments/exp4_time.py ; python experiments/exp4_stress.py ; python experiments/exp4_orderings.py
python experiments/exp4_horizon.py --games 30
python experiments/exp5_tournament.py ; python experiments/exp5_variants.py
python experiments/make_figures.py
```

Seed'ler betiklerin içinde sabittir (rastgele konumlar 4242 / 8080 / 4444, ağırlık ayarı 3000+i,
ufuk 7000+i, turnuva 900+i//2, Zobrist 20241142).

## Kontrol noktaları için hazır komutlar

| kontrol | komut |
|---|---|
| 0: perft | `python experiments/exp0_perft.py --pos "3 3 4 4 5 5" --pos "…" --nmax 4` |
| 1: kazan / kaybetme | `python -c "from game import *; from search import *; g=my_game(); print(minimax_decision(g, g.play('3 3 4 4 5 5'), 4))"` |
| 2: β koşulu | `python -m unittest discover -s tests -p "test_alphabeta.py" -v` |
| 3: Eval elle | `python evaluate.py "<hamle dizisi>"` (öznitelik sayıları, ağırlıklar, ham toplam, tanh) |
| 4: 1 s derinlik | `data/positions_stage4.txt` dosyasına konumları yazıp `python experiments/exp4_time.py --skip-correctness` |
| K = 5 / Misère vb. | `python agent.py --R 5 --C 8 --K 5 --V 2` ya da `Game(...)` parametreleri; tüm testler `python -m unittest discover -s tests` |

# Aşama 5: yerel turnuva (hamle başına 1 s, gerçek süreçler, ilk 2 hamle seed'li rastgele, seed 900+i//2)

Makine: Intel64 Family 6 Model 186 Stepping 2, GenuineIntel | Python 3.12.6 | Windows 11 (5 oyun paralel)

| rakip | oyun | G | B | M | G (önce/ikinci) | ort. hamle | ana ajan maks süre (s) | rakip maks süre (s) |
|---|---|---|---|---|---|---|---|---|
| Rastgele | 10 | 10 | 0 | 0 | 5/5 | 18.1 | 0.653 | 0.111 |
| Derinlik 2 α-β | 10 | 9 | 1 | 0 | 4/5 | 35.5 | 0.704 | 0.132 |
| Föy ayarı: sıralama c, uzatmasız | 10 | 5 | 0 | 5 | 0/5 | 34.4 | 0.734 | 0.715 |
| Uzatmasız (sıralama d) | 10 | 4 | 0 | 6 | 0/4 | 34.9 | 0.774 | 0.749 |
| Ağırlık C | 10 | 5 | 0 | 5 | 1/4 | 35.2 | 0.716 | 0.697 |
| MCTS (bonus) | 20 | 15 | 0 | 5 | 6/9 | 34.5 | 0.662 | 0.671 |

Ana ajanın en yavaş hamlesi: 0.774 s (soğuk başlatma dahil). Süre aşımı: 0, yasa dışı/geçersiz hamle: 0.

## Kaybedilen oyunlar (21)

* Föy ayarı: sıralama c, uzatmasız, oyun 0 (ana ajan önce): `3 5 5 5 7 6 5 5 0 4 0 0 7 7 7 7 2 2 2 3 2 2 3 0 0 1 1 1 1 1 6 6 6 6 3` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* Föy ayarı: sıralama c, uzatmasız, oyun 2 (ana ajan önce): `6 4 0 7 5 0 0 0 0 2 2 6 6 2 3 1 1 1 7 7 7 7 1 1 6 5 6 5 2 2 5 5 3 3 3 3 4` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* Föy ayarı: sıralama c, uzatmasız, oyun 4 (ana ajan önce): `4 6 0 7 0 5 6 3 1 2 1 6 7 7 7 7 0 1 1 1 6 6 2 2 2 2 5 5 5 5 0` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* Föy ayarı: sıralama c, uzatmasız, oyun 6 (ana ajan önce): `0 1 7 5 6 6 6 6 6 0 0 7 0 0 7 7 7 4 5 1 1 5 5 5 1 1 4 4 2 3 4 4 2 2 2 2 3` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* Föy ayarı: sıralama c, uzatmasız, oyun 8 (ana ajan önce): `4 6 0 7 0 5 6 3 1 2 1 6 7 7 7 7 0 1 1 1 6 6 2 2 2 2 5 5 5 5 0` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* Uzatmasız (sıralama d), oyun 0 (ana ajan önce): `3 5 5 0 0 0 7 6 1 1 1 7 7 6 6 6 6 2 3 7 7 4 1 1 5 4 0 0 5 3 3 3 2` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* Uzatmasız (sıralama d), oyun 2 (ana ajan önce): `6 4 0 7 5 1 7 7 7 7 0 1 2 3 2 0 0 0 1 5 6 3 5 4 6 2 2 2 5 5 3 3 1 1 3` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* Uzatmasız (sıralama d), oyun 3 (ana ajan ikinci): `6 4 7 0 1 7 7 2 6 0 1 2 0 7 7 0 0 5 1 4 4 6 6 6 4 4 2 2 2 1 1 3` — oyuncu 2 K'lık dizi yaptı (Misère: kaybeder)
* Uzatmasız (sıralama d), oyun 4 (ana ajan önce): `4 6 0 7 0 5 6 1 2 3 6 0 0 0 1 1 4 2 6 4 3 3 7 7 7 7 1 1 3 3 4 4 2` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* Uzatmasız (sıralama d), oyun 6 (ana ajan önce): `0 1 7 0 0 0 0 7 7 7 7 6 5 2 6 1 2 6 3 3 2 4 4 1 6 6 2 4 4 4 1 1 5 2 3` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* Uzatmasız (sıralama d), oyun 8 (ana ajan önce): `4 6 0 7 0 5 6 1 3 2 6 7 7 4 1 1 1 1 0 4 2 2 7 7 6 6 2 2 4 4 0` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* Ağırlık C, oyun 0 (ana ajan önce): `3 5 5 0 0 0 7 0 0 7 7 7 7 1 2 1 4 6 6 6 2 6 6 5 1 1 1 2 5 2 2 5 3 3 3 3 4` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* Ağırlık C, oyun 4 (ana ajan önce): `4 6 0 0 0 0 0 7 5 7 6 1 1 1 7 7 7 1 1 6 2 5 6 6 2 5 4 2 2 2 5 5 4 3 3` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* Ağırlık C, oyun 6 (ana ajan önce): `0 1 7 0 0 0 0 7 7 7 7 1 2 6 3 6 1 1 1 5 4 6 6 6 5 5 2 2 2 5 5 2 3 3 3 3 4` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* Ağırlık C, oyun 7 (ana ajan ikinci): `0 1 0 7 7 7 7 7 1 2 1 6 6 5 3 6 5 0 0 3 5 6 6 0 3 1 1 5 5 3 3 2 2 2 2 4` — oyuncu 2 K'lık dizi yaptı (Misère: kaybeder)
* Ağırlık C, oyun 8 (ana ajan önce): `4 6 0 0 0 0 0 7 5 7 6 1 1 1 7 7 7 1 1 6 2 5 6 6 2 5 4 2 2 2 5 5 4 3 3` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* MCTS (bonus), oyun 0 (ana ajan önce): `3 5 5 6 0 0 0 0 0 5 6 5 5 2 1 2 6 6 6 1 1 1 1 2 7 7 7 4 7 7 2 2 3 3 3 3 4` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* MCTS (bonus), oyun 6 (ana ajan önce): `0 1 7 5 6 6 6 3 6 0 6 7 0 7 1 0 0 5 7 1 7 1 1 5 5 5 3 3 3 3 2 4 2 2 2 2 4` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* MCTS (bonus), oyun 10 (ana ajan önce): `5 5 0 2 1 6 7 6 5 7 4 0 0 6 0 2 7 7 0 3 7 2 5 5 1 3 1 3 2 2 3 3 4 4 1` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* MCTS (bonus), oyun 16 (ana ajan önce): `0 6 7 0 0 4 0 0 7 2 4 7 4 7 7 6 1 1 1 1 1 6 2 2 2 2 5 4 4 3 3 3 3 3 6 6 5` — oyuncu 1 K'lık dizi yaptı (Misère: kaybeder)
* MCTS (bonus), oyun 19 (ana ajan ikinci): `3 6 2 2 2 2 2 7 6 6 7 7 6 6 7 7 3 5 3 0 1 0 1 0 1 5 5 5 5 1 1 3 3 0` — oyuncu 2 K'lık dizi yaptı (Misère: kaybeder)

### Analiz: Föy ayarı: sıralama c, uzatmasız, oyun 0

Her ana ajan hamlesi için 6 s'lik derin arama (değerler ana ajanın gözüyle):

| hamle no | oynanan | konum değeri | derinlik | derin aramanın hamlesi | oynanan hamle sonrası değer | derinlik |
|---|---|---|---|---|---|---|
| 3 | 5 | +0.000 | 8 | 0 | -0.083 | 9 |
| 5 | 7 | -0.042 | 8 | 0 | -0.083 | 9 |
| 7 | 5 | -0.083 | 8 | 5 | -0.124 | 9 |
| 9 | 0 | -0.124 | 9 | 0 | -0.124 | 9 |
| 11 | 0 | -0.245 | 10 | 7 | -0.245 | 10 |
| 13 | 7 | -0.245 | 11 | 0 | -0.283 | 10 |
| 15 | 7 | -0.321 | 14 | 7 | -0.245 | 13 |
| 17 | 2 | -0.659 | 13 | 0 | -1.000 | 13 |
| 19 | 2 | -0.635 | 13 | 0 | -1.000 | 12 |
| 21 | 2 | -0.205 | 10 | 0 | -1.000 | 11 |
| 23 | 3 | -0.321 | 9 | 0 | -1.000 | 9 |
| 25 | 0 | -0.394 | 9 | 0 | -1.000 | 7 |
| 27 | 1 | -0.394 | 5 | 6 | -1.000 | 6 |
| 29 | 1 | -0.494 | 5 | 1 | -1.000 | 6 |
| 31 | 6 | -1.000 | 1 | 6 | -1.000 | 1 |
| 33 | 6 | -1.000 | 1 | 6 | -1.000 | 1 |
| 35 | 3 | -1.000 | 1 | 3 | -1.000 | 0 |

İlk hata: 17. hamle (2 oynandı; derin arama 0 öneriyor, değer -0.659, derinlik 13).

```
. . . . . O . O
. . . . . X . X
O . . . . O . O
X . . . . X . X
X . . X O O O X
0 1 2 3 4 5 6 7
```

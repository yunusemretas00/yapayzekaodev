# Aşama 4.3: ufuk etkisi (D0 = 4, doğrulayıcı derinlik = 9, uzatma = 4)

Makine: Intel64 Family 6 Model 186 Stepping 2, GenuineIntel | Python 3.12.6 | Windows 11

Kendi kendine 30 oyunda bulunan kötü hamle (kanıtlanmış kayba giden, kaçınılabilir): 10; bunların 8 tanesini uzatma düzeltiyor.

## Örnek konum (sıra MAX (X)'da)

Hamle dizisi: `0 0 3 4 0 0 0 7 7 7 7 7 5 6 6 6 3 1 2 1 2 6 6 1`

```
X . . . . . X O
O . . . . . O X
X O . . . . O O
O O X X . . X X
X O X X O X O O
0 1 2 3 4 5 6 7
```

| derinlik | seçilen hamle | kök değeri (MAX gözüyle) |
|---|---|---|
| 4 | 2 | -0.165 |
| 5 | 3 | -0.462 |
| 6 | 2 | -0.165 |
| 7 | 2 | -0.462 |
| 8 | 2 | -0.245 |
| 9 | 5 | -0.761 |

D0 = 4'te seçilen 2, derinlik 9 doğrulamasında -1 (kanıtlanmış kayıp). Doğru hamle 5 (değer -0.761).

D0 = 4 + uzatma(4) ile seçilen hamle: 3 (değer -0.462) -> kötü hamleden kaçınıyor.

## Önce / sonra (derinlik 4, 60 oyun, eşli açılışlar)

| ajan | galibiyet | kötü hamle sayısı | hamle başına düğüm | hamle başına süre (ms) |
|---|---|---|---|---|
| uzatmasız (önce) | 21 | 7 | 206 | 3 |
| uzatma=4 (sonra) | 36 | 3 | 1,187 | 21 |

Beraberlik: 3.

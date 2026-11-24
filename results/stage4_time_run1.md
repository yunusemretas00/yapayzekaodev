# Aşama 4: zaman sınırlı arama

Makine: Intel64 Family 6 Model 186 Stepping 2, GenuineIntel | Python 3.12.6 | Windows 11 (gc arama sırasında kapalı)

## A) 20 konum, hamle başına 1.0 s

| ayar | ort. derinlik | min | maks | ort. düğüm | düğüm/s | en yavaş hamle (s) |
|---|---|---|---|---|---|---|
| tablo kapalı | 9.20 | 8 | 12 | 155,069 | 158,603 | 2.023 |
| tablo açık | 11.95 | 10 | 16 | 153,496 | 181,055 | 1.006 |
| tablo açık + uzatma(4) | 9.95 | 8 | 16 | 147,639 | 178,553 | 1.007 |

## B) Kontrol noktası 4: 10 konum, ajan ayarı (tablo + uzatma, iç bütçe 0.8 s)

| konum | taş sayısı | hamle | derinlik | değer | düğüm | süre (s) |
|---|---|---|---|---|---|---|
| T1 | 18 | 1 | 16 | +1.000 | 136,076 | 0.462 |
| T2 | 22 | 5 | 10 | -0.394 | 23,087 | 0.079 |
| T3 | 2 | 0 | 8 | +0.000 | 120,000 | 0.807 |
| T4 | 25 | 5 | 10 | +0.042 | 4,006 | 0.013 |
| T5 | 2 | 3 | 8 | +0.000 | 117,000 | 0.805 |
| T6 | 5 | 0 | 8 | +0.000 | 114,000 | 0.800 |
| T7 | 17 | 2 | 11 | -1.000 | 72,502 | 0.347 |
| T8 | 13 | 4 | 9 | -0.124 | 115,000 | 0.806 |
| T9 | 7 | 7 | 8 | +0.000 | 115,000 | 0.800 |
| T10 | 19 | 7 | 14 | +0.525 | 198,000 | 0.801 |

## C) Tablo doğruluğu

Tablo açıkken derinlik-6 değeri düz α-β ile 50/50 konumda aynı.

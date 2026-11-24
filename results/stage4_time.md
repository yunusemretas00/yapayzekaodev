# Aşama 4: zaman sınırlı arama

Makine: Intel64 Family 6 Model 186 Stepping 2, GenuineIntel | Python 3.12.6 | Windows 11 (gc arama sırasında kapalı)

## A) 20 konum, hamle başına 1.0 s

| ayar | ort. derinlik | min | maks | ort. düğüm | düğüm/s | en yavaş hamle (s) |
|---|---|---|---|---|---|---|
| tablo kapalı | 9.25 | 8 | 13 | 156,869 | 160,079 | 1.835 |
| tablo açık | 12.00 | 10 | 16 | 156,096 | 185,505 | 1.006 |
| tablo açık + uzatma(4) | 10.10 | 8 | 16 | 153,089 | 185,220 | 1.011 |

## B) Kontrol noktası 4: 10 konum, ajan ayarı (tablo + uzatma, iç bütçe 0.8 s)

| konum | taş sayısı | hamle | derinlik | değer | düğüm | süre (s) |
|---|---|---|---|---|---|---|
| T1 | 18 | 1 | 16 | +1.000 | 136,076 | 0.446 |
| T2 | 22 | 5 | 10 | -0.394 | 23,087 | 0.082 |
| T3 | 2 | 0 | 8 | +0.000 | 122,000 | 0.801 |
| T4 | 25 | 5 | 10 | +0.042 | 4,006 | 0.013 |
| T5 | 2 | 3 | 8 | +0.000 | 119,000 | 0.801 |
| T6 | 5 | 0 | 8 | +0.000 | 118,000 | 0.803 |
| T7 | 17 | 2 | 11 | -1.000 | 72,502 | 0.324 |
| T8 | 13 | 4 | 9 | -0.124 | 120,000 | 0.805 |
| T9 | 7 | 7 | 8 | +0.000 | 119,000 | 0.801 |
| T10 | 19 | 7 | 14 | +0.525 | 204,000 | 0.800 |

## C) Tablo doğruluğu

Tablo açıkken derinlik-6 değeri düz α-β ile 50/50 konumda aynı (1. koşu, stage4_time_run1.md).

Not: 1. koşuda (stage4_time_run1.md) tablo kapalı ayarda bir hamle 2.02 s sürdü; aynı konum 5 kez tekrarlandığında 1.002-1.005 s ölçüldü (işletim sistemi kaynaklı tek seferlik duraklama).

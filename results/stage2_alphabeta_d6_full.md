# Aşama 2: α-β ve hamle sıralaması (derinlik 6, eval=full, seed=4242)

R=5, C=8, K=4, V=2 (Misère), d=42, engelli=[]

Makine: Intel64 Family 6 Model 186 Stepping 2, GenuineIntel | Python 3.12.6 | Windows 11

Doğruluk: 50 konumun 50'inde α-β değeri = minimax değeri, seçilen hamlenin değeri = kök değeri ve α-β düğüm ≤ minimax düğüm (uyuşmazlık sayısı: 0).

| yöntem | ort. düğüm | geom. ort. | minimax'a oran (ort.) | b_etkin (geom.) | ort. süre (ms) | sıralama çağrısı (µs) | doğru |
|---|---|---|---|---|---|---|---|
| minimax | 186,242 | 162,257 | 100 % | 7.39 | 1282 | - | - |
| a: sıralamasız | 6,100 | 5,244 | 4.3 % | 4.17 | 38.7 | 0.1 | 50 |
| b: merkezden dışarı | 14,958 | 13,122 | 9.6 % | 4.86 | 97.0 | 0.7 | 50 |
| c: kazan/engelle + merkez | 11,988 | 10,092 | 7.2 % | 4.65 | 96.5 | 4.3 | 50 |
| d: c + Misère'de kenardan içe | 3,925 | 3,496 | 2.4 % | 3.90 | 34.8 | 6.3 | 50 |
| e: Eval tabanlı | 1,644 | 1,556 | 1.1 % | 3.40 | 47.2 | 45.7 | 50 |

Kuramsal en iyi sıralama ≈ sqrt(minimax düğümü) ≈ b^(m/2): ortalama 419 düğüm (c sıralaması bunun 28.6 katı).

En az budanan konum (c, oran 0.263): `5 1 1 5 0 0 2 6 5 1 1 0 4 0 1 2 4 5 0 6`

En çok budanan konum (c, oran 0.0206): `3 5 7 1 4 3 3 4 4`

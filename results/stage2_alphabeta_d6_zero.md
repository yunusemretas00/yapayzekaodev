# Aşama 2: α-β ve hamle sıralaması (derinlik 6, eval=zero, seed=4242)

R=5, C=8, K=4, V=2 (Misère), d=42, engelli=[]

Makine: Intel64 Family 6 Model 186 Stepping 2, GenuineIntel | Python 3.12.6 | Windows 11

Doğruluk: 50 konumun 50'inde α-β değeri = minimax değeri, seçilen hamlenin değeri = kök değeri ve α-β düğüm ≤ minimax düğüm (uyuşmazlık sayısı: 0).

| yöntem | ort. düğüm | geom. ort. | minimax'a oran (ort.) | b_etkin (geom.) | ort. süre (ms) | sıralama çağrısı (µs) | doğru |
|---|---|---|---|---|---|---|---|
| minimax | 186,242 | 162,257 | 100 % | 7.39 | 369 | - | - |
| a: sıralamasız | 1,506 | 1,446 | 1.0 % | 3.36 | 3.4 | 0.1 | 50 |
| b: merkezden dışarı | 1,568 | 1,519 | 1.0 % | 3.39 | 4.9 | 0.9 | 50 |
| c: kazan/engelle + merkez | 1,375 | 1,323 | 0.9 % | 3.31 | 8.1 | 4.7 | 50 |
| d: c + Misère'de kenardan içe | 1,389 | 1,334 | 0.9 % | 3.32 | 9.6 | 8.0 | 50 |
| e: Eval tabanlı | 1,415 | 1,371 | 0.9 % | 3.33 | 12.0 | 9.3 | 50 |

Kuramsal en iyi sıralama ≈ sqrt(minimax düğümü) ≈ b^(m/2): ortalama 419 düğüm (c sıralaması bunun 3.3 katı).

En az budanan konum (c, oran 0.033): `5 1 1 5 0 0 2 6 5 1 1 0 4 0 1 2 4 5 0 6`

En çok budanan konum (c, oran 0.0055): `5 7 3 0 3 5 0 6 7 3`

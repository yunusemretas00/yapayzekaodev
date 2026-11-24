# Aşama 3: ağırlık ayarı (derinlik 5 α-β, sıralama c, ilk 4 hamle rastgele, seed = 3000+i)

Makine: Intel64 Family 6 Model 186 Stepping 2, GenuineIntel | Python 3.12.6 | Windows 11

Ağırlık vektörleri:

| ağırlık | f1 | f2 | f3 | f4 | f5 | f6 |
|---|---|---|---|---|---|---|
| A | -1.00 | -0.25 | +1.00 | +0.25 | +0.00 | +0.50 |
| B | +1.00 | +0.25 | -1.00 | -0.25 | +0.15 | +0.00 |
| C | -0.50 | +0.00 | +0.50 | +0.00 | +0.00 | +1.50 |

Satır = ağırlık vektörü, sütun = rakip, hücre = satırın 20 oyundaki galibiyet/beraberlik/mağlubiyeti (10 oyun önce başlayarak + 10 oyun ikinci).

| vektör | A | B | C | toplam galibiyet | tahmin |
|---|---|---|---|---|---|
| **A** | — | 19 G / 0 B / 1 M | 17 G / 0 B / 3 M | 36 | en iyi ya da C ile başa baş |
| **B** | 1 G / 0 B / 19 M | — | 2 G / 0 B / 18 M | 3 | en kötü (Misère'de standart işaretler kendini dizmeye iter) |
| **C** | 3 G / 0 B / 17 M | 18 G / 0 B / 2 M | — | 21 | A'ya yakın; zugzwang sonlarında daha iyi |

İlk başlayan kazandı: 24, ikinci kazandı: 36, beraberlik: 0 (toplam 60 oyun, 8 s duvar saati, 14 paralel süreç).
En yavaş hamle: 0.43 s.

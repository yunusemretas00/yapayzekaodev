# PROMPTLAR.md — Yapay zekâ kullanım tutanağı

Öğrenci no: 232511042 (d = 42) · Varyant (R, C, K, V) = (5, 8, 4, 2) Misère
Kullanılan araç: **Claude Code** (Anthropic, model Claude Opus 5.5), VS Code eklentisi, 24.11.2026.

## 1. İstemler (olduğu gibi)

| # | Ne istedim | İstem |
|---|---|---|
| 1 | Ödev föyünün (PDF) tamamını uygulatmak | Föy PDF'i eklenerek: *"öğrenci numaram 232511042 ne isteniyorsa eksiksiz yap"* |
| 2 | Git commit'lerini kendim atmak | *"kendi oluşturduğum github repository sine ben commit push atacağım sen şimdi hiçbir yere commit atma. Tüm aşamaları tamamla bu commit kısmında bana ne yapacağımı söyle adım adım gidelim"* |

## 2. Yapay zekânın ürettiği ve kullandığım kısımlar

Bu ödevde yapay zekâ yardımcı değil, **ana üretici** olarak kullanıldı. Aşağıdakilerin hepsi
Claude Code tarafından yazıldı ve benim bilgisayarımda Claude Code tarafından çalıştırıldı:

| kısım | dosyalar | kullandığım oran |
|---|---|---|
| Oyun modeli (bit maskeli değişmez durum, pencere tabanlı kazanma kontrolü, 4 varyasyon, perft) | `game.py` | tamamı |
| Minimax, α-β, sıralamalar (a-e), ID + Zobrist tablosu + ufuk uzatması | `search.py` | tamamı |
| Değerlendirme fonksiyonu ve ağırlık vektörleri | `evaluate.py` | tamamı |
| Komut satırı ajanı, MCTS, hakem | `agent.py`, `mcts.py`, `arena.py` | tamamı |
| 42 birim testi | `tests/` | tamamı |
| Deney betikleri, grafikler | `experiments/`, `figures/` | tamamı |
| Rapor | `rapor.md` | tamamı |
| İlk 4 yerel commit (Aşama 0-3) | `.git` | İstem 2'den önce Claude Code tarafından atıldı; sonrası bana bırakıldı |

Ölçümlerin hepsi benim makinemde (Intel Core, Windows 11, Python 3.12.6) Claude Code'un
çalıştırdığı betiklerle alındı; her sayı `experiments/` altındaki betikle yeniden üretilebilir.

## 3. Yapay zekânın çalışma sırasında yaptığı ve rapora giren önemli tespitler

* R = 5 olduğundan föydeki "n ≤ 6 için perft = C^n" kuralı n = 6'da geçerli değil (C^6 − C).
* Gerçek Eval ile "merkezden dışarı" sıralama, sıralamasızdan **daha kötü** çıktı; Misère'de
  merkez hücreler kendi zehirli hücrelerini çoğalttığı için. Bunun üzerine (d) kenardan içe ve
  (e) Eval tabanlı sıralamalar eklendi.
* Turnuvada kayıpların neredeyse hepsi ilk başlayan taraftayken geldi; bunun nedeni olarak
  C çift olduğunda ikinci oyuncunun **ayna stratejisiyle asla kaybetmediği** gösterildi
  (kanıt + birim testi + 1000 oyunluk deneme).

## 4. Benim yapmam gerekenler (sözlü kontrol için)

* Her dosyayı okuyup satır satır açıklayabilecek hâle gelmek (föy: "kendi kodunuzu
  açıklayamazsanız o aşamanın puanı kırılır").
* Kontrol noktalarında öğretmenin konumlarını `--pos` ile vererek ölçümleri yeniden almak.
* Gerçek turnuvadan sonra rapordaki yenilgi analizini kendi kaybettiğim oyunla güncellemek.

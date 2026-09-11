# FluentPath 1.0 Mimari Özeti

- `main.py`: uygulama başlangıcı
- `app/curriculum.py`: A1-C2 ders ve placement içeriği
- `app/database.py`: SQLite, XP, streak, kilit, SRS, başarımlar, istatistik
- `app/services.py`: TTS, konuşma benzerliği ve writing değerlendirmesi
- `app/styles.py`: dark/light tema
- `app/ui.py`: tüm ekranlar ve akışlar

## Veri modeli

Profil, seviyeler, dersler, ders ilerlemesi, kelime tekrarı, çalışma logları,
beceri skorları, başarımlar ve placement sonuçları SQLite içinde tutulur.

## Seviye ilerleme

- Kullanıcı A1'den başlarsa yalnız A1 açıktır.
- Placement sonucunda B1 gibi bir seviye gelirse A1/A2/B1 erişilebilir olur.
- Bir seviyedeki 50 ders tamamlanınca bir sonraki seviye otomatik açılır.
- Bir ders açılmadan önce önceki dersin tamamlanması gerekir.

## SRS

Kelime ders tamamlanınca kelime havuzuna girer. Zor/Orta/Kolay değerlendirmesine göre
sonraki tekrar tarihi değişir.


## v2.2 Müfredat Ölçeği
- Her CEFR seviyesinde 50 ders vardır.
- 6 seviye x 50 ders = 300 ders.
- Her seviyede 10 ana ünite bulunur; her ünite ana ders + 4 pekiştirme dersiyle toplam 5 derslik yapıdadır.

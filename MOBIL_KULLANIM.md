# 12/D Dil Programı — Telefon Kullanımı

## Aynı Wi-Fi üzerinden hızlı kullanım

1. PC uygulamasını aç.
2. Sağ üst `☰` → **📱 Telefon Modu**.
3. Telefonda gösterilen `http://192.168.x.x:5050` adresini aç.
4. 6 haneli bağlantı kodunu gir.
5. Profilini seç ve kullan.

Alternatif olarak PC arayüzünü açmadan `MOBIL_BASLAT.bat` çalıştırabilirsin.

## Android

Chrome → sağ üst üç nokta → **Ana ekrana ekle**. HTTPS yayınında **Uygulamayı yükle** seçeneği de görünür.

## iPhone

Safari → Paylaş → **Ana Ekrana Ekle**.

## Veri paylaşımı

PC ve telefon aynı `data/fluentpath.db` dosyasını kullanır. Ders tamamlama, XP, kelimeler ve sınıf planları iki tarafta aynıdır. Mobil profil seçimi telefon oturumunda tutulur; PC'de açık olan profili zorla değiştirmez.

## 7/24 / dışarıdan erişim

Yerel modda bilgisayar açık olmalıdır. Okul dışında veya bilgisayar kapalıyken de kullanmak için mobil sunucuyu VPS'te HTTPS alan adıyla yayınlamak gerekir. PWA manifest ve service worker bu sürümde hazırdır.

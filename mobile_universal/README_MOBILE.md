# 12/D Dil Programı v5.1 — Universal Mobile

Bu klasör tarayıcı/PWA değildir. Aynı Python/Kivy kaynak kodundan Android ve iPhone/iPad uygulaması üretmek için hazırlanmıştır.

## Masaüstü sürümünden taşınan işlevler

- 5 saniyelik premium splash ve kredi yazısı
- İlk açılışta zorunlu profil oluşturma
- Çoklu profil oluşturma / değiştirme / silme
- Öğretmen ve öğrenci profilleri
- A1, A2, B1, B2, C1, C2 — her seviyede 50 ders, toplam 300 ders
- Ders kilitleri ve seviye ilerletme
- Grammar, kelime kartları, Reading, Listening, Speaking, Writing
- Ders sonu tüm quiz soruları ve %67 geçme şartı
- XP, günlük seri, günlük hedef
- Kelime Merkezi, favoriler, telaffuz
- Akıllı kelime tekrar sistemi (Zor / Orta / Kolay)
- Listening Lab
- Speaking Studio
- Reading Room
- Writing Coach
- İlerleme / beceri puanları / 7 günlük istatistik
- Başarımlar
- Profil ve uygulama ayarları
- A1→C2 seviye tespit sınavı
- Sınıf oluşturma / silme
- Sınıfa 50 dersten ders planı ekleme
- Ders planını Bekliyor ↔ İşlendi değiştirme ve silme
- Koyu / açık tema
- Telefonun kendi SQLite veritabanında çevrimdışı çalışma

## Android

Windows + WSL/Ubuntu üzerinde `ANDROID_APK_OLUSTUR.bat` çalıştır. APK `mobile_universal/bin/` içine gelir.

## iPhone / iPad

iOS uygulaması derlemek ve gerçek iPhone'a IPA yüklemek Apple gereği macOS + Xcode gerektirir. Projeyi Mac'e kopyala ve:

```bash
cd mobile_universal/ios
./BUILD_IOS_XCODE.sh
```

Script Xcode projesini oluşturur. Ardından Apple Team / Signing seçerek iPhone'da çalıştırabilir veya TestFlight/App Store paketi üretebilirsin.

## Speaking farkı

Android'de uygulama içi native konuşma tanıma düğmesi vardır. iPhone'da Speaking metin alanına dokunup iOS klavyesinin yerleşik mikrofon/dikte düğmesini kullanabilirsin. Puanlama ve öğrenme kaydı iki platformda aynıdır.

## Veri konusu

Mobil sürüm masaüstüyle aynı SQLite şemasını kullanır ancak telefonun sandbox'ında ayrı bir veritabanı tutar. Otomatik PC↔telefon canlı senkronizasyonu için bir sunucu/hesap sistemi gerekir; bu v5.0 paketinin dışında tutulmuştur.

## Güncel build notları

Android builder `p4a.branch = develop`, Android API 36 ve NDK 29 kullanır. iOS builder güncel Kivy iOS akışındaki `toolchain build kivy` ve `toolchain create <title> <app_directory>` düzenini kullanır. iOS derlemesi Windows'ta yapılamaz; macOS ve Xcode gerekir.

## v5.0.1 Android Build Fix

Bu paket eski `android_native` klasörünü kaldırır. Android APK üretmek için sadece
`mobile_universal/ANDROID_APK_OLUSTUR.bat` veya paketin kökündeki
`ANDROID_APK_OLUSTUR.bat` kullanılmalıdır.

Yeni Android build hattı:
- Python target/host: 3.14.2
- p4a: develop
- Android API: 36
- min API / NDK API: 24
- NDK: 29
- ABI: yalnızca arm64-v8a
- Buildozer: güncel GitHub master
- Java: OpenJDK 17
- Tam build logu: `mobile_universal/android_build.log`

Eski logda `requirements=python3,kivy,plyer` veya `armeabi-v7a` görüyorsan yanlış/eski
builder çalıştırılmış demektir. v5.0.1 bu eski builder'ı paket içinde tutmaz.


## v5.1 iPhone / iPad paketleme geliştirmeleri

- iPhone ve iPad için tek tık `IOS_XCODE_OLUSTUR.command`
- Kivy-iOS resmi akışını kullanan `toolchain build kivy`
- Xcode projesini otomatik oluşturan `toolchain create`
- iPhone, iPad ve App Store ikon seti
- Mikrofon / speech recognition izin açıklamaları
- `tr.okul.dilprogrami12d` bundle identifier
- iOS 13.0 minimum deployment target
- Xcode proje doğrulaması
- iOS build logu
- iOS cache temizleme aracı

Android ve iOS aynı `mobile_universal/main.py` ve `mobile_app/` çekirdeğini kullanır.


## v5.3 Stabilite

Özellikle düşük/orta ekranlı Android cihazlarda yazı taşması ve ders açma
çökmesi için ders ekranı yeniden düzenlendi. Uygulama alanındaki
`mobile_error.log`, yakalanan mobil UI hatalarını tutar.

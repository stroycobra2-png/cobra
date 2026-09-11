# 12/D Dil Programı v4.0 — Native Android

Bu klasör tarayıcı/PWA değildir. Kivy ile hazırlanmış, Android'e APK olarak
paketlenebilen gerçek mobil uygulama sürümüdür.

## Mobilde bulunan temel özellikler

- İlk açılışta zorunlu profil oluşturma
- Öğretmen / öğrenci profilleri
- Profil değiştirme ve silme
- A1-C2 seviyeleri
- Her seviyede 50 ders, toplam 300 ders
- Ders kilit sistemi ve XP
- Kelime tekrar sistemi
- Sınıf oluşturma
- Sınıf ders planı
- Android TTS ile listening metinlerini seslendirme
- Premium koyu mobil arayüz
- Yerel SQLite: internet ve PC olmadan çalışır

## APK nasıl üretilir?

Windows'ta Android derleme araçları doğrudan Python ile rahat çalışmadığı için
önerilen yöntem WSL/Ubuntu + Buildozer'dır.

1. Windows'ta WSL + Ubuntu kur.
2. Bu projenin `android_native` klasörüne gir.
3. `ANDROID_APK_OLUSTUR.bat` çalıştır.
4. İlk derleme Android SDK/NDK indireceği için uzun sürebilir.
5. Başarılı olursa APK `android_native/bin/` klasöründe oluşur.
6. APK'yı telefona gönderip kur.

## Önemli

Bu Android sürümü yerel çalışır; telefonun kendi SQLite veritabanını kullanır.
Bu yüzden PC açık olmak zorunda değildir.

PC ile otomatik internet üzerinden senkronizasyon istiyorsan sonraki adımda
hesap/senkron API'si eklenebilir.


## v4.0.1 WSL Builder Fix

- `where wsl` artik tek basina yeterli kabul edilmiyor.
- Gercek Linux komut testi yapiliyor.
- Ubuntu dagitimi yoksa derleme baslatilmiyor.
- `WSL_UBUNTU_KUR.bat` eklendi.
- `WSL_TEST.bat` eklendi.
- Windows -> WSL klasor yolu guvenli bicimde `wslpath` ile cevriliyor.
- Ic ice tirnak kullanan eski WSL komutu kaldirildi.
- `BUILD_APK.sh` kendi klasorune otomatik geciyor ve Python venv kullaniyor.
- Derleme basarisizsa BAT artik yanlis sekilde "APK hazir" demiyor.


## v4.0.2 WSL Build Fix

Önceki sürümde `.buildvenv` klasörü yarım oluştuğunda
`.buildvenv/bin/activate: No such file or directory` hatası alınabiliyordu.

Yeni builder:

- yarım sanal ortamı otomatik algılar ve yeniden oluşturur,
- Python venv'i Windows `/mnt/c` alanında değil Linux `$HOME` altında tutar,
- tüm Android build işlemini `$HOME/.12d_android_builder/project` içinde yapar,
- Windows yolundaki boşluk ve Türkçe karakterlerin Buildozer'a etkisini azaltır,
- derlenen APK'yı otomatik olarak Windows `android_native/bin` klasörüne kopyalar,
- `ANDROID_BUILD_CACHE_TEMIZLE.bat` ile Linux build cache'i güvenli biçimde sıfırlanabilir.


## v4.0.3 — Python 3.14 / python-for-android Fix

Bu sürüm Ubuntu 26.04 / Python 3.14 ortamı için Android build zincirini yeniler:

- Buildozer GitHub master sürümü
- `p4a.branch = develop`
- Android API 36
- Android NDK r28c
- Rust / Cargo kurulumu
- `legacy-cgi`
- `cython==0.29.34`
- OpenJDK 17 zorlaması
- WSL içindeki Windows Java/PATH girdilerinin build sırasında temizlenmesi
- eski `p4a master` checkout ve build dist cache'lerinin temizlenmesi

Önce doğrudan `ANDROID_APK_OLUSTUR.bat` çalıştır.
Eğer eski cache'in tamamen sıfırlanmasını istersen önce
`P4A_PY314_ONAR.bat`, sonra `ANDROID_APK_OLUSTUR.bat` çalıştır.

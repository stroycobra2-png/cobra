# 12/D Dil Programı v2.2 — 300 DERS TEACHER EDITION

A1-C2 İngilizce öğrenme masaüstü uygulaması.

Açılış ekranı: **Made By Hacı Bozkurt / The Teacher Pelin Doğan Ortaç**

## v1.1'de yeni
- Ana sayfada doğrudan sıradaki derse devam
- Günlük XP / çalışma özeti
- Hızlı Listening, Speaking, Writing ve Review kısayolları
- Son çalışma geçmişi
- Ders arama ve durum filtreleme
- Kelime arama, favori filtresi ve tek tık favorileme
- Kelimeye çift tıklayarak telaffuz dinleme
- Review ekranında cevap görülmeden puanlama yapılamaması
- Aktif sol menü vurgusu
- Sidebar günlük durum özeti
- Son 7 gün çalışma görünümü
- Seviye testini ayarlardan yeniden çalıştırma
- Klavye kısayolları

## Kurulum
1. ZIP'i temiz bir klasöre çıkar.
2. `KURULUM.bat` dosyasını çalıştır.
3. Kurulum bittikten sonra `BASLAT.bat` dosyasını çalıştır.

## Kısayollar
- Ctrl+1: Ana Sayfa
- Ctrl+2: Dersler
- Ctrl+3: Kelimeler
- Ctrl+R: Tekrar
- Ctrl+F: Ders ara
- F5: Sayfaları yenile

Mevcut `data/fluentpath.db` dosyanı bu sürümün `data` klasörüne kopyalarsan ilerlemen korunur.

## v1.1.1 Mikrofon düzeltmesi

- PyAudio bağımlılığı kaldırıldı.
- Mikrofon kaydı `sounddevice` + `numpy` ile alınır.
- SpeechRecognition artık ham ses verisini doğrudan işler.
- Speaking ekranı kayıt sırasında donmaz; kayıt arka iş parçacığında çalışır.
- `MIKROFON_TEST.bat` varsayılan Windows giriş aygıtını kontrol eder.
- `BASLAT.bat` eksik mikrofon paketlerini algılarsa requirements dosyasını otomatik kurar.

İlk kullanımda `KURULUM.bat` çalıştırılması önerilir.


## v1.2 Marka güncellemesi
- Uygulama adı: **12/D Dil Programı**
- Açılış splash ekranı eklendi.
- Açılışta **Made By Hacı Bozkurt / The Teacher Pelin Doğan Ortaç** yazısı gösterilir.
- EXE adı Windows uyumluluğu için `12D_Dil_Programi.exe` olarak oluşturulur.


## v1.3.1 — Animated Splash + Starfield
- Açılış ekranı tam **5 saniye** sürer.
- Splash ekranında hareketli Starfield parçacıkları vardır.
- Logo ve kredi yazısı sırayla fade-in animasyonu ile görünür.
- 5 saniyelik yükleme çubuğu bulunur.
- Son 0.6 saniyede splash fade-out olur ve ana pencere fade-in ile açılır.
- Ana uygulama arka planında düşük maliyetli, sürekli hareket eden Starfield particles bulunur.
- Starfield açık/koyu temaya uyum sağlar.
- Kartlar hafif transparan yapılarak yıldızlar arka planda görünür tutulur.


## v1.3.1 Stabilite ve tema düzeltmeleri
- QGraphicsOpacityEffect tamamen kaldırıldı.
- Starfield ve splash QPainter çakışması giderildi.
- 5 saniyelik splash gerçek zaman tabanlıdır.
- Açılış başlığı ve kredi yazısı kesilmeden görünür.
- Koyu tema Qt Palette + QSS birlikte kullanır.
- Dialog, QMessageBox, ComboBox popup, Table, Header, ScrollBar, StatusBar ve inputlar koyu temaya uyar.
- Açık -> koyu tema geçişinde tema tamamen yeniden uygulanır.


## v2.1 Premium Edition
- Premium dark/light visual system
- Gradient glass-style cards and controls
- Modern grouped navigation
- Premium top bar with level, streak, XP and avatar
- Animated nebula + starfield background
- Premium 5-second splash refresh
- Redesigned sidebar brand and current-level card
- More consistent typography, spacing, pills, progress bars and input styling
- Stable painter architecture preserved; QGraphicsOpacityEffect is not used


## v2.1 — Öğretmen / Sınıf Yönetimi
- Sağ üstte **☰ yönetim menüsü** eklendi.
- Birden fazla öğretmen/öğrenci profili oluşturulabilir ve değiştirilebilir.
- Her profilin XP, seviye, ders ilerlemesi, kelimeleri, tekrarları ve istatistikleri ayrıdır.
- Profil türü: Öğretmen / Öğrenci.
- Sınıf oluşturma: sınıf adı, CEFR seviyesi, eğitim-öğretim yılı ve sınıf notu.
- Her sınıfa müfredattan işlenecek ders atanabilir.
- Ders planına tarih ve öğretmen notu eklenebilir.
- Dersler Bekliyor / İşlendi olarak takip edilir.
- Sınıflar aktif profile özeldir.


## v2.2 — 300 Ders Müfredatı
- A1: **50 ders**
- A2: **50 ders**
- B1: **50 ders**
- B2: **50 ders**
- C1: **50 ders**
- C2: **50 ders**
- Toplam: **300 ders**
- Her seviyede 10 ana ünite vardır. Her ana ünite; ana ders, Kelime Atölyesi, Grammar Lab, Reading & Listening ve Speaking & Writing çalışmalarıyla desteklenir.
- İlk 10 ana dersin position değerleri korunur; eski ilerleme verilerinin uyumluluğu gözetilir.
- Sınıf Yönetimi ekranı yeni 50 derslik seviye listelerini otomatik kullanır.


## v2.2.1 Sidebar Fix
- Sol alt Current Level kartı 50 derslik sistem için yeniden tasarlandı.
- Kart artık `tamamlanan / toplam ders • yüzde` bilgisini açıkça gösterir.
- Günlük dakika/tekrar bilgileri bu dar karttan kaldırıldı; taşma/kesilme engellendi.
- Sol üst marka alanına `Made By Hacı Bozkurt / The Teacher Pelin Doğan Ortaç` eklendi.


## v2.2.2 — Sol Üst Marka Kartı Düzeltmesi

- Sol üst marka kartındaki metin kaymaları düzeltildi.
- Kart yüksekliği sabitlendi.
- Logo ve başlık aynı üst satırda tutuldu.
- Kredi yazısı ayrı, tam genişlikli iki satıra taşındı.
- `PREMIUM LEARNING` rozeti ayrı alt satıra alındı.
- Sidebar genişliği 282 px'e çıkarıldı.
- Koyu ve açık temada tipografi/padding yeniden ayarlandı.


## v2.3 — İlk Açılışta Zorunlu Profil

- Temiz kurulumda otomatik/boş profil oluşturulmaz.
- 5 saniyelik splash sonrasında profil yoksa zorunlu profil ekranı açılır.
- Profil oluşturulmadan ana pencere oluşturulmaz ve gösterilmez.
- Zorunlu profil penceresi kapatılırsa uygulama kapanır.
- İlk profil oluşturulunca aktif profil olarak SQLite veritabanına kaydedilir.
- Sonraki açılışlarda profil bulunduğu için ekran bir daha gösterilmez.
- Sağ üst menüden daha sonra yeni profil oluşturma ve profil değiştirme devam eder.


## v2.3.1 — Profil Silme Düzeltmesi

- `En az bir profil kalmalıdır` kısıtlaması kaldırıldı.
- Son kalan profil de artık silinebilir.
- Profil silmeden önce zorunlu onay penceresi açılır.
- Onay metni: `Bu profili silmek istediğinize emin misiniz?`
- Varsayılan seçim `Hayır`dır.
- Son profil silinirse ana uygulama profilsiz açık kalmaz.
- Kullanıcı otomatik olarak zorunlu profil oluşturma ekranına yönlendirilir.
- Yeni profil oluşturulmazsa uygulama kapanır.


## v2.3.2 — Silinen Profilin Geri Gelmesi Düzeltildi

Sorunun kaynağı eski sürümden kalan `profile` tablosuydu. Son yeni profil
silindikten sonra uygulama yeniden açıldığında migration sistemi bu eski
kaydı tekrar `profiles` tablosuna taşıyabiliyordu.

Yeni davranış:
- Uygulama açılırken `profiles` tablosunun daha önce mevcut olup olmadığı tespit edilir.
- Yeni profil sistemi daha önce kullanılmışsa legacy `profile` kaydı bir daha migrate edilmez.
- Son profil silinip program kapatılıp tekrar açıldığında profil geri gelmez.
- Uygulama 0 profil durumunda kalır ve zorunlu profil oluşturma ekranını açar.
- Gerçekten eski, `profiles` tablosu hiç bulunmamış veritabanları ise bir kez migrate edilmeye devam eder.

# v3.0 — Telefon / PWA Entegrasyonu

Bu sürüm PC uygulamasını korur ve aynı SQLite veritabanına bağlı premium mobil arayüz ekler.

## Telefonu bağlama

1. `KURULUM.bat` çalıştır.
2. PC uygulamasında sağ üst `☰` menüsünden **📱 Telefon Modu** seç veya `MOBIL_BASLAT.bat` çalıştır.
3. PC ekranında/terminalde görünen `http://192.168.x.x:5050` adresini telefonda aç.
4. 6 haneli bağlantı kodunu gir.
5. Profilini seç ve kullan.

### Mobil özellikler

- Premium telefon arayüzü
- Profil seçme ve yeni profil oluşturma
- A1-C2, toplam 300 ders
- Ders kilitleri ve quizler
- Mobilde tamamlanan dersin PC veritabanına XP/ilerleme/kelime olarak yazılması
- Kelime merkezi ve favoriler
- Spaced repetition
- Telefonun TTS özelliğiyle Listening
- Destekleyen tarayıcılarda konuşmayı metne çevirme
- Sınıf ve ders planlarını görüntüleme
- Ders planını `Bekliyor / İşlendi` değiştirme
- PWA manifest + service worker
- 6 haneli mobil bağlantı kodu
- SQLite WAL/busy timeout ile PC + telefon eşzamanlı kullanım iyileştirmesi

Yerel Wi-Fi modunda bilgisayar açık kalmalıdır. Tam PWA kurulumu ve her yerden 7/24 erişim için HTTPS/VPS gerekir.


## v4.0 — Native Android

`android_native/` klasörü eklendi. Bu sürüm tarayıcı/PWA değil, Kivy ile
APK'ya dönüştürülebilen gerçek Android uygulamasıdır. Android uygulaması
telefonun kendi SQLite veritabanıyla bağımsız çalışır.


## v4.0.1 — Android Builder Fix

Windows'ta WSL yardim ekraninin acilmasina neden olan BAT tirnak/yol aktarimi duzeltildi. Ayrica WSL motoru ile gercek Ubuntu/Linux dagitimi ayri ayri kontrol ediliyor.


## v4.0.3 Android Builder

Ubuntu 26.04 / Python 3.14 için p4a develop + API 36 + NDK r28c ve OpenJDK 17
uyumluluk düzeltmeleri eklendi.


## v5.0 Universal Mobile
`mobile_universal/` klasörü Android + iPhone/iPad için tam mobil özellik setini içerir. Tarayıcı/PWA değildir.

## v5.0.1 — Android Build Düzeltmesi

Android tarafında eski `android_native` builder kaldırıldı. Tek doğru APK builder artık
`ANDROID_APK_OLUSTUR.bat` -> `mobile_universal/ANDROID_APK_OLUSTUR.bat` akışıdır.
Builder yalnızca arm64-v8a üretir ve Python 3.14.2 / p4a develop / API 36 / NDK 29
ayarlarını doğrulamadan derlemeye başlamaz.


## v5.1 — Android + iPhone/iPad Universal Mobile

`mobile_universal/` artık tek ortak mobil uygulama kaynak kodundan iki ayrı
native paketleme hattı sağlar:

- Android: `ANDROID_APK_OLUSTUR.bat`
- iPhone/iPad (Mac): `mobile_universal/ios/IOS_XCODE_OLUSTUR.command`

iOS tarafına otomatik Xcode projesi, iPhone/iPad/App Store icon seti,
bundle identifier ve izin açıklamaları eklendi.


## v5.2 — Windows'tan iPhone Cloud Build

Mac sahibi olmayan Windows kullanıcıları için GitHub Actions tabanlı iOS
derleme hattı eklendi.

- `.github/workflows/ios-cloud-build.yml`
  - Apple signing olmadan Kivy-iOS/Xcode projesini ve Simulator build'i doğrular.
- `.github/workflows/ios-signed-ipa.yml`
  - Apple sertifika ve provisioning secrets ayarlandığında imzalı IPA export etmeyi dener.
- `WINDOWS_IPHONE_CLOUD_BUILD.md`
  - Windows üzerinden adım adım kullanım kılavuzu.

Yerel Windows iOS derlemesi yapılmaz; macOS/Xcode işlemleri GitHub'ın macOS
runner'ında gerçekleşir.


## v5.3 — Mobile Stability Fix

Telefon arayüzü için stabilizasyon güncellemesi:

- Ders açılırken oluşan UI exception'ları uygulamayı kapatmaz.
- `mobile_error.log` ile cihazdaki yakalanan Python/Kivy hataları kaydedilir.
- Ders ekranında JSON verileri güvenli okunur.
- Quiz Spinner sistemi kaldırıldı; mobil dokunmatik seçenek butonlarına geçildi.
- Ders listesi 10'ar derslik sayfalara bölündü.
- Sabit kartların dışına taşan yazılar sınırlandırıldı.
- Uzun ders metinleri otomatik yüksekliğe sahip kartlara taşındı.
- Emoji/font uyumsuzluğu yapabilen menü simgeleri sade metne dönüştürüldü.
- TTS çağrıları korumalı hale getirildi.
- Android log alma yardımcısı eklendi.


## v5.3.1 — Windows iPhone Build Merkezi

Windows kullanıcıları için iPhone build süreci ana pakete görünür biçimde
entegre edildi.

Ana klasörde:
- `IPHONE_BUILD_WINDOWS.bat` — tek merkez menüsü
- `IPHONE_WINDOWS_HIZLI_BASLANGIC.md`
- `WINDOWS_IPHONE_CLOUD_BUILD.md`
- `IPHONE_CLOUD_BUILD/` — görünür yardımcı klasör

Gerçek GitHub Actions workflow'ları:
- `.github/workflows/ios-cloud-build.yml`
- `.github/workflows/ios-signed-ipa.yml`

Eski `WINDOWS_IPHONE_BUILD_BILGI.bat` ve `IPHONE_WINDOWS_BILGI.bat`
dosyaları artık yeni build merkezini açar.


## v5.3.2 — IPHONE_OLUSTUR.bat

Windows iPhone build akışı tek bir `IPHONE_OLUSTUR.bat` dosyasında toplandı.

GitHub CLI (`gh`) kuruluysa BAT dosyası:
- GitHub girişini kontrol eder,
- repository oluşturabilir,
- proje dosyalarını push edebilir,
- `iOS Cloud Build` workflow'unu başlatabilir,
- Apple signing secrets ayarlıysa `iOS Signed IPA` workflow'unu başlatabilir,
- Actions sayfasını otomatik açabilir.

GitHub CLI yoksa indirme/rehber akışına yönlendirir.

Not: iOS derlemesinin kendisi Windows'ta yapılmaz; BAT GitHub'ın macOS
runner'ını tetikler.


## v5.3.3 — iPhone No-Install Windows Builder

`IPHONE_OLUSTUR.bat` artık Git veya GitHub CLI istemez.

Windows'un yerleşik PowerShell'i:
- GitHub hesabını token ile doğrular,
- private repository oluşturur/günceller,
- tüm proje dosyalarını GitHub Git Data API ile yükler,
- iOS workflow'unu başlatır,
- build durumunu otomatik takip eder,
- başarılı artifact'i `ios_output` klasörüne indirir.

Gerçek imzalı IPA modu da aynı BAT içindedir. Apple signing secrets eksikse
ilgili GitHub ayar sayfası otomatik açılır.


## v5.3.4 — Windows PowerShell Path Fix

- Windows PowerShell 5.1'de hata veren `TrimStart('\\','/')` kullanımı kaldırıldı.
- Dosya yolları artık regex ile güvenli biçimde normalize ediliyor.
- Boş GitHub repository ref sorgusunda oluşabilen HTTP 409 durumu destekleniyor.
- Repository yazma yetkisi için daha anlaşılır kontrol eklendi.
- Repository oluşturma 403 hatasına Türkçe yönlendirme eklendi.


## v5.3.5 — Türkçe Q / Unicode Fix
Android ve iPhone için Türkçe karakter normalizasyonu ve locale düzeltmeleri eklendi.


## v5.3.6 — Uygulama İçi Türkçe Q Klavye

Android ve iPhone/iPad için ortak, uygulama içi Türkçe Q klavye eklendi.
Metin kutuları `keyboard_mode=managed` kullanır; İngilizce sistem klavyesi
otomatik açılmaz. Shift, sayı/sembol, boşluk, silme ve Enter tuşları vardır.


## v5.3.7 — iPhone Empty Repository Fix

- GitHub repository tamamen boşsa otomatik ilk commit oluşturulur.
- Boş repo için GitHub Contents API kullanılır.
- Ardından Git blobs/trees/commits yükleme akışı devam eder.
- Yeni oluşturulan repository artık `auto_init=true` ile başlatılır.
- `.buildvenv`, `.gradle`, `node_modules`, `dist`, `build` gibi gereksiz yerel klasörler cloud upload dışında bırakılır.


## v5.3.8 — PowerShell Mode Variable Fix

- `$mode` ile `$Mode` çakışması düzeltildi.
- Git dosya izin modu artık `$gitFileMode` değişkeninde tutuluyor.
- `100644 / 100755` değerleri artık cloud/signed parametresine yazılmıyor.


## v5.3.9 — Android Startup Fix

Android APK'nın açılışta kapanmasına neden olan sınıf sıralaması hatası düzeltildi.

Eski durumda:
- `TurkishQKeyboard(Card)` sınıfı,
- `Card`, `PButton`, `SButton` tanımlanmadan önce çalıştırılıyordu.

Yeni durumda:
- `Card`
- `PButton`
- `SButton`
- `TurkishQKeyboard`

sırasıyla tanımlanıyor.

Uygulama içi Türkçe Q klavye, Unicode düzeltmeleri ve iPhone build sistemi korunmuştur.


## v5.3.10 — iPhone PowerShell Tree Array Fix

Windows PowerShell 5.1'de `.NET Generic.List[object]` ile
`@($TreeEntries)` dönüşümünün oluşturduğu
`ArgumentException / Bağımsız değişken türleri eşleşmiyor` hatası düzeltildi.

Artık:
- `$TreeEntries = @()` saf PowerShell array kullanır.
- Tree girdileri `+= @{ ... }` ile eklenir.
- GitHub tree body doğrudan `$TreeEntries` dizisini kullanır.


## v5.3.11 — iPhone Workflow 404 Fix

- Upload sonrası GitHub repository metadata yeniden okunur.
- Workflow dosyasının default branch'te bulunduğu doğrulanır.
- GitHub'ın yeni workflow'u indekslemesi 90 saniyeye kadar beklenir.
- Workflow dosya adı yerine numeric workflow ID ile tetiklenir.
- Disabled workflow otomatik etkinleştirilmeye çalışılır.
- Actions API izni yoksa doğrudan Türkçe hata gösterilir.


## v5.3.12 — iPhone Workflow Path Fix

- GitHub Contents API için `.github/workflows/...` yolu artık slash karakterleri `%2F` yapılmadan kullanılır.
- Contents API geçici olarak 404 dönerse recursive Git tree üzerinden ikinci doğrulama yapılır.
- Windows dosya taraması `Get-ChildItem -Force` kullanır; `.github` klasörü kesin dahil edilir.
- Upload başlamadan önce iki iOS workflow dosyasının yerelde bulunduğu doğrulanır.

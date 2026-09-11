# iPhone'u Windows'tan Direkt Oluştur — Ekstra Program Kurmadan

Ana klasörde sadece:

`IPHONE_OLUSTUR.bat`

çalıştır.

Bu sürüm **Git, GitHub CLI veya Mac kurulumu istemez**. Windows'un kendi
PowerShell'i GitHub REST API üzerinden projeyi private repository'ye yükler,
GitHub'ın macOS runner'ında iOS build'i başlatır, build'in bitmesini bekler ve
çıktıyı otomatik olarak `ios_output` klasörüne indirir.

## İlk kullanımda neden GitHub token gerekiyor?

GitHub'ın senin hesabında private repository oluşturmasına ve workflow
başlatmasına izin vermen gerekiyor. Bu bir program indirme değildir; GitHub
hesabının erişim anahtarıdır.

GitHub'da Personal Access Token oluştur. Private repo + workflow işlemleri için
gerekli repository/workflow izinlerini ver. Tokeni yalnızca
`IPHONE_OLUSTUR.bat` açıldığında çıkan gizli alana yapıştır.

**Tokeni bana gönderme ve proje dosyalarına yazma.**

## Menü

### 1 — iOS Cloud Build oluştur ve indir

- Projeyi otomatik GitHub'a yükler.
- macOS build'i başlatır.
- Kivy-iOS ve Xcode build'ini çalıştırır.
- Sonucu `ios_output/12D_Dil_Programi_iOS_Xcode_Project.zip` olarak indirir.

Bu mod Apple sertifikası istemeden iOS kodunun derlenmesini doğrular ama gerçek
iPhone'a kurulabilen imzalı IPA değildir.

### 2 — Gerçek imzalı iPhone IPA oluştur ve indir

Aynı otomasyon gerçek `.ipa` build'ini başlatır. Apple'ın güvenlik sistemi
nedeniyle şu GitHub Secrets değerleri repository'de bulunmalıdır:

- `IOS_CERTIFICATE_P12_BASE64`
- `IOS_CERTIFICATE_PASSWORD`
- `IOS_PROVISIONING_PROFILE_BASE64`
- `IOS_TEAM_ID`
- `IOS_KEYCHAIN_PASSWORD` (opsiyonel)

Eksikler varsa BAT otomatik olarak GitHub Secrets sayfasını açar. Bunlar bir
kez ayarlandıktan sonra sonraki IPA build'leri tek BAT ile başlatılır ve sonuç
`ios_output/12D_Dil_Programi_iPhone_IPA.zip` içine indirilir.

## Neden Apple signing tamamen kaldırılamıyor?

Android APK ile iPhone IPA arasındaki temel fark budur. Apple gerçek iPhone'da
çalışacak uygulamaların geçerli geliştirici sertifikası ve provisioning profile
ile imzalanmasını zorunlu tutar. Windows tarafındaki otomasyon bunu mümkün
olduğunca tek tıka indirir, fakat Apple hesabı/imzası yerine geçemez.


## v5.3.4 notu

Eski sürümde Windows PowerShell 5.1 `TrimStart` karakter dönüşümünde hata
verebiliyordu. Bu sürümde yol işleme regex tabanlı hale getirildi. Aynı
`cobra` repository adını yeniden kullanabilirsin.


## v5.3.7 — Boş repository otomatik düzeltme

`cobra` repository tamamen boş olsa bile artık elle README oluşturman gerekmez.
`IPHONE_OLUSTUR.bat` önce `.12d-init.txt` ile ilk commit'i otomatik oluşturur,
sonra iPhone proje dosyalarını GitHub'a yüklemeye devam eder.


## v5.3.8 — Mode değişkeni düzeltmesi

PowerShell büyük/küçük harf ayrımı yapmadığı için `$Mode` ve `$mode` aynı
değişken kabul ediliyordu. Git dosya izin modu artık `$gitFileMode` olarak
ayrı tutuluyor.


## v5.3.10 — PowerShell tree array düzeltmesi

Windows PowerShell 5.1'de GitHub tree oluştururken görülen
`Bağımsız değişken türleri eşleşmiyor` hatası giderildi.
.NET Generic List kaldırıldı ve saf PowerShell array kullanılmaya başlandı.

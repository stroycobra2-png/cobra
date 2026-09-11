# iPhone'u Windows'tan Derleme — Mac Sahibi Olmadan

Yerel Windows/WSL üzerinde iPhone `.ipa` derlenemez. Bunun nedeni Kivy değil,
Apple'ın iOS derleme zincirinin Xcode gerektirmesidir.

Bu projede Mac satın almadan kullanabileceğin bulut yöntemi hazırlandı:
**GitHub Actions macOS runner**.

## Seçenek 1 — Önce iOS projesinin derlenmesini doğrula

Bu işlem Apple sertifikası istemez.

1. GitHub'da yeni bir repository oluştur.
2. Bu ZIP'in içindeki TÜM dosyaları repository'ye yükle.
   `.github` klasörü de yüklenmiş olmalı.
3. GitHub repository sayfasında `Actions` sekmesine gir.
4. Soldan `iOS Cloud Build` seç.
5. `Run workflow` düğmesine bas.
6. Build tamamlanınca çalışma sayfasının en altındaki `Artifacts` bölümünden:
   `12D-Dil-Programi-iOS-Xcode-Project`
   dosyasını indir.

Bu workflow GitHub'ın macOS makinesinde:
- Xcode'u açar,
- Kivy-iOS kurar,
- Kivy'yi iOS için derler,
- 12/D Xcode projesini oluşturur,
- iPhone Simulator build'i yaparak kaynak kodun derlenmesini doğrular.

Bu çıktı **IPA değildir**; Apple imzası olmadan gerçek iPhone'a kurulamaz.

---

## Seçenek 2 — Windows'tan gerçek imzalı IPA üret

Bunun için Apple'ın iOS kod imzalama sistemi gereği Apple Developer
sertifikası ve provisioning profile gerekir.

Repository > Settings > Secrets and variables > Actions bölümüne aşağıdaki
GitHub Secrets değerlerini ekle:

- `IOS_CERTIFICATE_P12_BASE64`
- `IOS_CERTIFICATE_PASSWORD`
- `IOS_PROVISIONING_PROFILE_BASE64`
- `IOS_TEAM_ID`
- `IOS_KEYCHAIN_PASSWORD` (isteğe bağlı)

Ardından:

Actions > `iOS Signed IPA` > `Run workflow`

Başarılı olduğunda Artifacts bölümünde:

`12D-Dil-Programi-iPhone-IPA`

oluşur.

## Çok önemli güvenlik notu

`.p12` sertifikasını, sertifika şifresini veya provisioning profile içeriğini
sohbete, koda ya da normal GitHub dosyalarına koyma.

Bunlar yalnızca GitHub repository'nin `Secrets` bölümüne eklenmeli.

## Apple hesabı

Gerçek cihaz dağıtımı / TestFlight / App Store için Apple'ın provisioning ve
code-signing gereksinimleri geçerlidir. GitHub Actions sadece Mac bilgisayarın
yerine buluttaki macOS makinesini kullanır; Apple'ın imzalama şartlarını
ortadan kaldırmaz.

## Bundle ID

Bu projede:

`tr.okul.dilprogrami12d`

kullanılıyor.

Apple Developer tarafındaki App ID ve provisioning profile bu Bundle ID ile
eşleşmelidir.

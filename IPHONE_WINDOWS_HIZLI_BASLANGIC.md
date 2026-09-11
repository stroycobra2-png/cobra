# Windows'tan iPhone Oluştur

Artık ana klasörde yalnızca:

`IPHONE_OLUSTUR.bat`

dosyasını açman yeterli.

Menü:

1. iOS Cloud Build başlat
2. İmzalı IPA build başlat
3. GitHub repository oluştur ve projeyi yükle
4. Workflow dosyalarını kontrol et
5. GitHub Actions sayfasını aç
6. Ayrıntılı rehberi aç

## Tam otomasyon için

Windows'a GitHub CLI kur:

https://cli.github.com/

Ardından CMD/PowerShell'de bir kez:

`gh auth login`

yap.

Sonra `IPHONE_OLUSTUR.bat` içinden **3** seçeneğini kullanarak repository
oluşturabilir, ardından **1** ile iOS Cloud Build'i başlatabilirsin.

Gerçek imzalı `.ipa` için Apple signing secrets hâlâ gereklidir.
# iPhone Build — Windows Hızlı Başlangıç

Ana klasörde:

`IPHONE_BUILD_WINDOWS.bat`

dosyasını çalıştır.

Açılan menü şunları yapar:

1. Ayrıntılı Windows → iPhone rehberini açar.
2. `.github/workflows` altındaki iki iOS workflow dosyasını kontrol eder.
3. GitHub yeni repository sayfasını açar.
4. GitHub Actions sayfasını açar.
5. iOS yardımcı dosyalarının klasörünü açar.

## GitHub'a yüklenmesi gereken dosyalar

ZIP'i GitHub repository'ye yüklerken yalnızca `mobile_universal` klasörünü
değil, **paketin tamamını** yükle.

Özellikle şunlar bulunmalı:

```text
.github/
└── workflows/
    ├── ios-cloud-build.yml
    └── ios-signed-ipa.yml
```

GitHub Actions workflow'ları yalnızca `.github/workflows` konumundan algılar.

## İki iOS build türü

### iOS Cloud Build

Apple sertifikası gerekmeden Kivy-iOS/Xcode projesini ve Simulator build'ini
bulutta doğrular.

GitHub:

`Actions → iOS Cloud Build → Run workflow`

### iOS Signed IPA

Gerçek iPhone'a kurulabilecek imzalı IPA için Apple sertifikası ve provisioning
profile gerekir.

GitHub:

`Actions → iOS Signed IPA → Run workflow`

Ayrıntılar için:

`WINDOWS_IPHONE_CLOUD_BUILD.md`

# 12/D Dil Programı — iPhone / iPad Kurulumu

Bu sürüm tarayıcı değildir. Android ve iPhone/iPad aynı `mobile_universal`
Kivy uygulama kodunu kullanır.

## iPhone'da neler çalışır?

- İlk açılışta zorunlu profil
- Profil oluşturma / değiştirme / silme
- Öğretmen ve öğrenci profilleri
- A1-C2, her seviyede 50 ders, toplam 300 ders
- Ders kilitleri, XP, seri ve ders sonu quiz
- Kelime Merkezi ve Akıllı Tekrar
- Listening TTS
- Speaking puanlama
- Reading Room
- Writing Coach
- İlerleme, beceri puanları ve başarımlar
- Sınıf oluşturma / silme
- Sınıfa ders planı ekleme
- Bekliyor / İşlendi durumu
- Koyu / açık tema
- Çevrimdışı SQLite

## iPhone için neden Mac gerekiyor?

Apple'ın iOS uygulama derleme ve imzalama zinciri Xcode kullanır. Bu nedenle
iPhone/iPad için son paket Windows/WSL üzerinde üretilemez.

## Mac'te yapılacaklar

1. Xcode'u App Store'dan kur ve bir kez aç.
2. Proje ZIP'ini Mac'e çıkar.
3. Finder'da:
   `mobile_universal/ios/IOS_XCODE_OLUSTUR.command`
   dosyasına çift tıkla.
4. Script Kivy-iOS bağımlılıklarını kurar, Kivy dağıtımını derler ve
   Xcode projesini oluşturur.
5. Xcode'da `Signing & Capabilities > Team` bölümünden Apple hesabını seç.
6. iPhone'u kabloyla veya Xcode wireless debugging ile bağla.
7. iPhone'u hedef cihaz seçip Run'a bas.

TestFlight / App Store için Xcode'da `Product > Archive` kullanılır.

## Speaking notu

iPhone'da hedef cümleyi dinleme ve Speaking puanlama çalışır.
Konuşmayı metne geçirmek için iOS klavyesinin mikrofon/dikte özelliği
kullanılabilir. Android sürümünde ayrıca uygulama içi konuşma tanıma düğmesi vardır.

## Veriler

Mobil uygulama telefonun kendi uygulama alanında SQLite veritabanı tutar ve
internetsiz çalışır. PC ile canlı otomatik senkronizasyon ayrı bir hesap/bulut
sistemi gerektirir.

# Android Açılış Düzeltmesi — v5.3.9

APK'nın hiç açılmamasının nedeni bulundu.

`TurkishQKeyboard`, `Card` sınıfından türetilmişti fakat Python dosyasında
`Card` sınıfından önce tanımlanmıştı. Android uygulama başlatılırken Python
modülü import edildiği anda bu nedenle kapanıyordu.

v5.3.9'da sınıf sırası düzeltildi.

Korunan özellikler:
- uygulama içi Türkçe Q klavye
- İ / i / I / ı Unicode düzeltmeleri
- Android tr-TR locale
- iPhone tr/en localization
- iPhone Cloud Build

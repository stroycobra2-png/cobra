import sys

print('12/D Dil Programı Mikrofon Testi')
print('=' * 40)

try:
    import sounddevice as sd
except Exception as e:
    print('HATA: sounddevice yüklenemedi:', e)
    print('KURULUM.bat dosyasını yeniden çalıştır.')
    sys.exit(1)

try:
    default_in = sd.default.device[0]
    print('Varsayılan giriş cihazı ID:', default_in)
    if default_in is None or int(default_in) < 0:
        print('HATA: Varsayılan mikrofon seçili değil.')
        sys.exit(2)
    info = sd.query_devices(int(default_in), 'input')
    print('Mikrofon:', info['name'])
    print('Giriş kanalı:', info['max_input_channels'])
    print('Varsayılan sample rate:', info['default_samplerate'])
    print('\nMikrofon erişimi hazır görünüyor.')
except Exception as e:
    print('HATA:', type(e).__name__, e)
    sys.exit(3)

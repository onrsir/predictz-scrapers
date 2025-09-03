# İddia Meselesi Automation System

Bu sistem, web scrapers'larını otomatik çalıştırıp Firebase'e upload yapan tam otomatik bir çözümdür.

## 🚀 Özellikler

- **Otomatik Scraping**: Belirlenen zamanlarda scrapers'ları otomatik çalıştırır
- **Firebase Integration**: Scrape edilen verileri otomatik olarak Firebase'e upload eder
- **Cron Job Management**: Sistem cron job'larını otomatik yönetir
- **Monitoring Dashboard**: Web tabanlı izleme paneli
- **Logging**: Detaylı log sistemi
- **Hata Yönetimi**: Hataları yakalar ve bildirim gönderir
- **Configurable**: JSON tabanlı konfigürasyon sistemi

## 📦 Kurulum

### Gereksinimler

- Python 3.7+
- Node.js (Firebase upload script'leri için)
- crontab (macOS/Linux)

### İlk Kurulum

1. **Dependencies'leri kontrol edin**:
   ```bash
   # Python dependencies (mevcut scrapers'lar için)
   pip install requests beautifulsoup4 lxml

   # Node.js dependencies (Firebase için)
   cd ../Predictor
   npm install
   ```

2. **İlk test çalıştırması**:
   ```bash
   cd automation
   python automation.py run
   ```

3. **Otomatik çalıştırmayı etkinleştir**:
   ```bash
   python automation.py schedule install
   ```

4. **Monitoring dashboard'unu başlat**:
   ```bash
   python automation.py monitor
   ```

## 🎮 Kullanım

### Temel Komutlar

```bash
# Tüm scrapers'ları manuel çalıştır
python automation.py run

# Sadece predictz scraper'ını çalıştır
python automation.py run predictz

# Cron job'ları kur
python automation.py schedule install

# Aktif cron job'ları listele
python automation.py schedule list

# Cron job'ları kaldır
python automation.py schedule remove

# Test çalıştırması
python automation.py test predictz

# Web monitoring dashboard'unu başlat
python automation.py monitor

# Sistem durumunu göster
python automation.py status

# Konfigürasyonu görüntüle
python automation.py config
```

### Monitoring Dashboard

Dashboard'a erişim:
- URL: http://localhost:8080
- Otomatik yenileme: 5 dakikada bir
- Özellikler:
  - Son 7 günün istatistikleri
  - Başarı oranları
  - Son çalıştırmalar
  - Canlı log görüntüleme

Farklı port kullanmak için:
```bash
python automation.py monitor --port 8081
```

## ⚙️ Konfigürasyon

`automation_config.json` dosyası ilk çalıştırmada otomatik oluşturulur:

```json
{
    "scrapers": {
        "predictz": {
            "enabled": true,
            "class_name": "PredictzScraper",
            "schedule": ["08:00", "20:00"]
        }
    },
    "firebase": {
        "auto_upload": true,
        "delete_after_upload": false
    },
    "logging": {
        "level": "INFO",
        "max_file_size": "10MB",
        "backup_count": 5
    },
    "notifications": {
        "enabled": false,
        "email": {
            "smtp_server": "",
            "port": 587,
            "username": "",
            "password": "",
            "to_addresses": []
        }
    }
}
```

### Konfigürasyon Seçenekleri

#### Scrapers
- `enabled`: Scraper'ı aktif/pasif yapar
- `schedule`: Günlük çalıştırma saatleri (HH:MM formatında)

#### Firebase
- `auto_upload`: Scraping sonrası otomatik Firebase upload
- `delete_after_upload`: Upload sonrası JSON dosyalarını sil

#### Notifications
- Email bildirimleri için SMTP ayarları
- Şu anda sadece log'a yazıyor, ileride email/Slack eklenebilir

## 📊 Çalıştırma Programı

Default schedule (günde 2 kez):
- 08:00 - Sabah çalıştırması
- 20:00 - Akşam çalıştırması

Kendi schedule'ınızı config dosyasından değiştirebilirsiniz.

## 📝 Logging

Log dosyaları `logs/` dizininde saklanır:
- Format: `automation_YYYYMM.log`
- Otomatik rotation
- 30 gün sonra otomatik silinir

Log seviyeleri:
- `DEBUG`: Detaylı debug bilgileri
- `INFO`: Genel bilgilendirme
- `WARNING`: Uyarılar
- `ERROR`: Hatalar

## 🔧 Troubleshooting

### Yaygın Sorunlar

**1. Cron job kurulum hatası**
```bash
# Mevcut crontab'ı kontrol et
crontab -l

# Manuel olarak düzenle
crontab -e
```

**2. Firebase upload hatası**
- Node.js dependencies'lerini kontrol edin
- Firebase config'ini kontrol edin
- Network bağlantısını kontrol edin

**3. Permission hatası**
```bash
# Script'leri executable yap
chmod +x automation.py
chmod +x automation_manager.py
chmod +x scheduler.py
```

**4. Path sorunları**
- Script'leri tam path ile çalıştırın
- Python path'ini kontrol edin

### Debug

Detaylı debug için log seviyesini değiştirin:
```json
{
    "logging": {
        "level": "DEBUG"
    }
}
```

## 📁 Dosya Yapısı

```
automation/
├── automation.py              # Ana komut arayüzü
├── automation_manager.py      # Otomasyon manager
├── scheduler.py              # Cron job yöneticisi
├── monitor_dashboard.py      # Web monitoring
├── automation_config.json    # Konfigürasyon (otomatik oluşur)
├── logs/                     # Log dosyaları
│   └── automation_202508.log
├── results/                  # Çalıştırma sonuçları
│   └── automation_result_20250826_120000.json
└── README.md                # Bu dosya
```

## 🔄 Güncelleme

Sistem güncellemeleri için:

1. **Yeni scraper eklemek**:
   - Scraper class'ını import edin
   - `run_scraper()` methodunu güncelleyin
   - Config'e yeni scraper'ı ekleyin

2. **Notification sistemi eklemek**:
   - `send_notification()` methodunu geliştirin
   - Email/Slack entegrasyonu ekleyin

3. **Dashboard geliştirmek**:
   - `monitor_dashboard.py`'yi düzenleyin
   - Yeni metrikleri ekleyin

## 🎯 Roadmap

- [ ] Email/Slack notification desteği
- [ ] Daha fazla scraper desteği
- [ ] Database logging
- [ ] API endpoint'leri
- [ ] Docker containerization
- [ ] Health check endpoint'leri

## 📞 Destek

Sorun yaşadığınızda:
1. `python automation.py status` ile sistem durumunu kontrol edin
2. Log dosyalarını inceleyin
3. Debug mode'da çalıştırın
4. Manuel test yapın: `python automation.py test predictz`

## 📜 Lisans

Bu proje özel kullanım içindir.

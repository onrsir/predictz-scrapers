# Football Prediction Scrapers ⚽🏈

Football maçları için tahmin verilerini çeşitli sitelerden toplayan otomatik scraper sistemi.

## 🚀 Özellikler

- **Predictz.com** tahmin verilerini otomatik çekme
- **Firebase** entegrasyonu ile cloud storage
- **Otomatik scheduling** ve monitoring
- **JSON** formatında veri depolama
- **Log** sistemi ve hata raporlama

## 📁 Proje Yapısı

```
scrapers/
├── predictz_scraper.py      # Predictz.com scraper
├── automation/              # Otomasyon sistemi
│   ├── automation_manager.py    # Ana otomasyon yöneticisi
│   ├── automation_scheduler.py  # Zamanlama sistemi
│   ├── automation_config.json   # Yapılandırma dosyası
│   ├── logs/                    # Log dosyaları
│   └── results/                 # Sonuç dosyaları
├── scripts/                 # Yardımcı scriptler
│   └── import-predictz-data.sh  # Shell script
├── data/                    # Çekilen veriler (gitignore'da)
├── requirements.txt         # Python bağımlılıkları
└── README.md               # Bu dosya
```

## ⚙️ Kurulum

### 1. Repository'yi klonlayın
```bash
git clone https://github.com/YOUR_USERNAME/football-prediction-scrapers.git
cd football-prediction-scrapers
```

### 2. Python virtual environment oluşturun
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# veya
venv\Scripts\activate   # Windows
```

### 3. Bağımlılıkları yükleyin
```bash
pip install -r requirements.txt
```

### 4. Data klasörünü oluşturun
```bash
mkdir -p data
```

## 🔧 Kullanım

### Tek Seferlik Scraping
```bash
# Sadece Predictz verilerini çek
python3 predictz_scraper.py

# Shell script ile çek
./scripts/import-predictz-data.sh
```

### Tam Otomasyon (Scraping + Firebase Upload)
```bash
# Otomatik scraping ve Firebase upload
python3 automation/automation_manager.py
```

### Belirli Scraper'ı Çalıştırma
```bash
# Sadece predictz
python3 automation/automation_manager.py predictz
```

## 📊 Veri Formatı

### Predictz Çıktı Formatı
```json
{
  "scraper": "predictz",
  "generated_at": "2025-09-04T01:00:00",
  "data_by_date": {
    "2025-09-05": [
      {
        "league_name": "Premier League Tips",
        "matches": [
          {
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "prediction": "Home 2-1",
            "match_date": "20250905"
          }
        ]
      }
    ]
  }
}
```

## 🔥 Firebase Entegrasyonu

Sistem Firebase'e otomatik veri yükleyebilir. Bunun için:

1. Firebase credentials'larınız olması gerekiyor
2. `automation/automation_config.json` dosyasında Firebase ayarları aktif olmalı
3. Upload script path'i doğru ayarlanmalı

## ⚙️ Yapılandırma

`automation/automation_config.json` dosyasında ayarları değiştirebilirsiniz:

```json
{
  "scrapers": {
    "predictz": {
      "enabled": true,
      "schedule": ["08:00", "20:00"]
    }
  },
  "firebase": {
    "auto_upload": true,
    "delete_after_upload": false
  },
  "logging": {
    "level": "INFO"
  }
}
```

## 📝 Loglar ve Sonuçlar

- **Loglar**: `automation/logs/automation_YYYYMM.log`
- **Sonuçlar**: `automation/results/automation_result_YYYYMMDD_HHMMSS.json`
- **Data dosyaları**: `data/predictz_*.json` (gitignore'da)

## 🐛 Hata Ayıklama

### Yaygın Sorunlar

1. **403 Forbidden**: Site access engellemiş, IP değiştirin veya daha sonra deneyin
2. **Module not found**: Virtual environment aktif mi kontrol edin
3. **Firebase upload error**: Credentials ve script path'i kontrol edin

### Debug Modu
```bash
# Detaylı loglar için
export PYTHONPATH="."
python3 automation/automation_manager.py
```

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📜 Lisans

Bu proje [MIT License](LICENSE) altında lisanslanmıştır.

## 📞 İletişim

- **Geliştirici**: Onur Şir
- **GitHub**: [@onursir](https://github.com/onursir)

## 🔄 Desteklenen Siteler

- ✅ **Predictz.com** - Football match predictions
- 🔜 **Diğer siteler** - Gelecekte eklenecek

## 📈 Performans

- **Ortalama scraping süresi**: ~30-40 saniye
- **Veri hacmi**: Günde ~50-150 maç
- **Desteklenen lig sayısı**: 20+ lig
- **Firebase upload**: ~15 saniye

---

⭐ **Bu projeyi faydalı buluyorsanız, lütfen bir yıldız bırakın!**

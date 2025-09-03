# Predictz Scraper Güncellemeleri

## 📅 25 Ağustos 2025 - Çoklu Tarih Desteği

### 🎯 Yapılan Değişiklikler

#### 1. Çoklu Tarih Desteği
- **Öncesi**: Sadece yarın (`tomorrow/`) sayfasından veri çekiyordu
- **Sonrası**: Yarından başlayarak 4 günlük veri çeker
- **Format**: `https://www.predictz.com/predictions/YYYYMMDD/` formatında URL'ler kullanır

#### 2. Gelişmiş Veri Yapısı
```json
{
    "scrape_timestamp": "2025-08-25T12:12:18.740612",
    "dates_scraped": ["20250825", "20250826", "20250827", "20250828"],
    "data_by_date": {
        "20250825": [...],
        "20250826": [...],
        "20250827": [...],
        "20250828": [...]
    }
}
```

#### 3. İyileştirilmiş Dosya Sistemi
- **Tarih bazında dosyalar**: `predictz_data_2025-08-25.json`
- **Birleştirilmiş dosya**: `predictz_combined_2025-08-25.json`
- **Her maç için tarih bilgisi**: `match_date` alanı eklendi

#### 4. Shell Script Desteği
```bash
./scripts/import-predictz-data.sh
```

### 🔧 Teknik Detaylar

#### Python Scraper (`predictz_scraper.py`)
- **Yeni metod**: `generate_date_list()` - 4 günlük tarih listesi oluşturur
- **Güncellenmiş metod**: `get_page_content(date_str)` - Belirli tarih için veri çeker
- **Gelişmiş parsing**: Her maç için tarih bilgisi eklendi
- **Rate limiting**: İstekler arasında 10 saniye bekleme
- **Hata yönetimi**: Başarısız tarihler atlanır, başarılı olanlar işlenir

#### Shell Script (`scripts/import-predictz-data.sh`)
- Otomatik sanal ortam aktivasyonu
- Hata kontrolü ve durum raporlama
- Dosya sayım ve özet raporu
- Renkli çıktı ve emoji destekli arayüz

### 📊 Çıktı Formatı

#### Başarılı Çalıştırma Örneği:
```
🚀 Predictz Data Import Script
================================
🐍 Python sanal ortamı aktivasyonu...
📅 Bugünden başlayarak 4 günlük veri çekiliyor...

==================================================
Tarih: 20250825 işleniyor...
==================================================
✅ Tarih 20250825: 47 maç, 9 lig
📁 Kaydedildi: data/predictz_data_2025-08-25.json

🎉 İşlem tamamlandı!
📊 Özet:
   • Başarılı tarihler: 3/4
   • Toplam maç sayısı: 150
   • Birleştirilmiş dosya: data/predictz_combined_2025-08-25.json
```

### 🗃️ Dosya Yapısı

```
scrapers/
├── predictz_scraper.py          # Ana scraper (güncellenmiş)
├── predictz_scraper.py.backup   # Yedek kopya
├── scripts/
│   └── import-predictz-data.sh  # Shell script (yeni)
└── data/
    ├── predictz_data_2025-08-25.json      # Bugün
    ├── predictz_data_2025-08-26.json      # Yarın
    ├── predictz_data_2025-08-27.json      # Öbür gün
    ├── predictz_data_2025-08-28.json      # 3 gün sonra
    └── predictz_combined_2025-08-25.json  # Hepsi bir arada
```

### 🎮 Kullanım

#### Doğrudan Python ile:
```bash
cd /path/to/scrapers
source venv/bin/activate
python3 predictz_scraper.py
```

#### Shell script ile:
```bash
./scripts/import-predictz-data.sh
```

### ⚠️ Önemli Notlar

1. **403 Hataları**: Site bazı tarihler için kısıtlama yapabilir, bu normal
2. **Rate Limiting**: İstekler arasında 10 saniye beklenir
3. **Veri Formatı**: Her maçta `match_date` alanı bulunur
4. **Yedekleme**: Eski versiyon `.backup` uzantısıyla saklandı

### 🆔 Çekilecek Tarihler

- **Yarın**: 26 Ağustos 2025 (`20250826`)
- **Öbür gün**: 27 Ağustos 2025 (`20250827`) 
- **3 gün sonra**: 28 Ağustos 2025 (`20250828`)
- **4 gün sonra**: 29 Ağustos 2025 (`20250829`)

### 📈 Performans İyileştirmeleri

- ✅ Paralel olmayan sıralı işleme (site koruması için)
- ✅ Hata durumunda diğer tarihler işlenmeye devam eder  
- ✅ Ayrıntılı ilerleme raporlama
- ✅ Birleştirilmiş ve tarih bazında dosya seçenekleri
- ✅ Otomatik dizin oluşturma

Bu güncellemeler ile artık predictz.com'dan 4 günlük kapsamlı veri çekimi yapılabilmektedir.

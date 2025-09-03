# Rate Limiting Güncellemesi

## 📅 25 Ağustos 2025 - Bekleme Süresi Güncellemesi

### ⏱️ Yapılan Değişiklik

**Rate Limiting Artırıldı**: İstekler arasındaki bekleme süresi 10 saniye olarak güncellendi

#### Önceki Durum:
```python
time.sleep(random.uniform(1, 2))  # 1-2 saniye rastgele bekleme
```

#### Yeni Durum:
```python
time.sleep(10)  # Sabit 10 saniye bekleme
```

### 🎯 Özellikler

#### 1. Sabit Bekleme Süresi
- Her tarih arası geçişte sabit 10 saniye bekleme
- Rastgele süre yerine öngörülebilir timing

#### 2. Görsel Progress Indicator
```
⏳ Sonraki tarih (20250827) için 10 saniye bekleniyor...
⏱️  10 saniye kaldı...
⏱️  9 saniye kaldı...
⏱️  8 saniye kaldı...
...
⏱️  1 saniye kaldı...
✅ Bekleme tamamlandı!
```

#### 3. Akıllı Bekleme Kontrolü
- Son tarih işlendiğinde bekleme yapılmaz
- Sadece bir sonraki tarih varsa countdown başlar

### 📊 Örnek Çıktı

```
==================================================
Tarih: 20250826 işleniyor...
==================================================
Tarih 20250826 için veri çekiliyor: https://www.predictz.com/predictions/20250826/
✅ Tarih 20250826: 54 maç, 18 lig
📁 Kaydedildi: data/predictz_data_2025-08-26.json

⏳ Sonraki tarih (20250827) için 10 saniye bekleniyor...
⏱️  10 saniye kaldı...
⏱️  9 saniye kaldı...
⏱️  8 saniye kaldı...
⏱️  7 saniye kaldı...
⏱️  6 saniye kaldı...
⏱️  5 saniye kaldı...
⏱️  4 saniye kaldı...
⏱️  3 saniye kaldı...
⏱️  2 saniye kaldı...
⏱️  1 saniye kaldı...
✅ Bekleme tamamlandı!

==================================================
Tarih: 20250827 işleniyor...
==================================================
```

### 🔧 Teknik Detaylar

#### Rate Limiting Mantığı:
```python
# Bir sonraki tarihe geçmeden önce sıradaki tarihle devam edip etmeyeceğini kontrol et
next_index = self.dates_to_scrape.index(date_str) + 1
if next_index < len(self.dates_to_scrape):
    next_date = self.dates_to_scrape[next_index]
    print(f"⏳ Sonraki tarih ({next_date}) için 10 saniye bekleniyor...")
    for i in range(10, 0, -1):
        print(f"\r⏱️  {i} saniye kaldı...", end="", flush=True)
        time.sleep(1)
    print("\r✅ Bekleme tamamlandı!     ")
```

### 🎯 Faydalar

1. **Site Koruması**: Daha uzun bekleme süresi ile site rate limiting'ini önler
2. **Görsel Geri Bildirim**: Kullanıcı bekleme süresini takip edebilir  
3. **Akıllı Yönetim**: Gereksiz bekleme yapmaz (son tarihte)
4. **Öngörülebilir Timing**: Sabit süre ile toplam çalışma süresini hesaplamak kolay

### ⏳ Toplam Süre Hesaplaması

4 tarihin çekilmesi için beklenen süre:
- **Veri çekme**: ~2-5 saniye/tarih
- **Bekleme**: 10 saniye × 3 geçiş = 30 saniye
- **Toplam**: ~35-50 saniye (4 tarih için)

### ✅ Kullanım

Güncellenmiş scraper ile çalışma aynı şekilde:

```bash
# Shell script ile
./scripts/import-predictz-data.sh

# Doğrudan Python ile
source venv/bin/activate
python3 predictz_scraper.py
```

Bu güncelleme ile scraper daha güvenli ve görsel olarak daha informatif hale geldi.

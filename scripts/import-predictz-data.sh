#!/bin/bash

# import-predictz-data.sh
# Predictz.com'dan 4 günlük maç tahmin verilerini çeken script

echo "🚀 Predictz Data Import Script"
echo "================================"

# Script dizinini belirle
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Python script'inin yerini kontrol et
PYTHON_SCRIPT="$PROJECT_DIR/predictz_scraper.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Hata: predictz_scraper.py bulunamadı: $PYTHON_SCRIPT"
    exit 1
fi

# Python sanal ortamını kontrol et
VENV_PATH="$PROJECT_DIR/venv"
if [ -d "$VENV_PATH" ]; then
    echo "🐍 Python sanal ortamı aktivasyonu..."
    source "$VENV_PATH/bin/activate"
else
    echo "⚠️  Uyarı: Python sanal ortamı bulunamadı, sistem Python'u kullanılıyor"
fi

# Data klasörünü oluştur
mkdir -p "$PROJECT_DIR/data"

echo "📅 Yarından başlayarak 4 günlük veri çekiliyor..."
echo "📍 Çalışma dizini: $PROJECT_DIR"

# Python script'ini çalıştır
cd "$PROJECT_DIR"
python3 "$PYTHON_SCRIPT"

# Çıkış kodu kontrol et
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Scraping işlemi başarıyla tamamlandı!"
    
    # Dosya sayısını göster
    DATA_FILES=$(ls -1 data/predictz_data_*.json 2>/dev/null | wc -l)
    COMBINED_FILES=$(ls -1 data/predictz_combined_*.json 2>/dev/null | wc -l)
    
    echo "📊 Sonuç:"
    echo "   • Tarih bazında dosyalar: $DATA_FILES"
    echo "   • Birleştirilmiş dosyalar: $COMBINED_FILES"
    echo "   • Veri klasörü: $PROJECT_DIR/data"
    
    # Son dosyaları listele
    echo ""
    echo "📁 Son oluşturulan dosyalar:"
    ls -lt data/predictz_*.json | head -5
    
else
    echo "❌ Scraping işleminde hata oluştu!"
    exit 1
fi

echo ""
echo "🏁 İşlem tamamlandı."

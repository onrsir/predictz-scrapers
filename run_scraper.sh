#!/bin/bash

# İddia Meselesi Manuel Scraper
echo "🎯 İddia Meselesi Scraper Başlatılıyor..."

# Ana dizine git
cd "/Users/onursir/Documents/iddia meselesi/scrapers"

# Virtual environment aktif et
echo "🐍 Python virtual environment aktifleştiriliyor..."
source venv/bin/activate

# Automation manager'ı çalıştır
echo "🤖 Automation manager çalıştırılıyor..."
cd automation
python automation_manager.py predictz

echo "✅ İşlem tamamlandı!"
echo "📊 Sonuçları automation/results/ klasöründe görebilirsiniz"
echo "📝 Logları automation/logs/ klasöründe görebilirsiniz"

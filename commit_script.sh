#!/bin/bash

# Git repo oluştur (eğer zaten yoksa)
if [ ! -d ".git" ]; then
    git init
    echo "Git repo oluşturuldu."
fi

# Dosyaları git'e ekle
git add predictz_scraper.py test_scraper.py requirements.txt README.md .gitignore

# Commit oluştur
git commit -m "predictz.com web scraper oluşturuldu"

echo "Git commit işlemi tamamlandı." 
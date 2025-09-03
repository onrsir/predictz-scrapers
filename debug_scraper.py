#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import os

def download_and_save_html():
    """
    Web sayfasını indir ve debug için kaydet
    """
    url = "https://www.predictz.com/predictions/tomorrow/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Debug klasörünü oluştur
        if not os.path.exists("debug"):
            os.makedirs("debug")
            
        # HTML'i kaydet
        with open("debug/page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        # HTML yapısını analiz et ve bazı bilgileri çıkar
        analyze_html_structure(response.text)
        
        print(f"HTML başarıyla kaydedildi: debug/page.html")
        return True
        
    except requests.RequestException as e:
        print(f"Hata: Web sayfası indirilemedi - {e}")
        return False
        
def analyze_html_structure(html_content):
    """
    HTML yapısını analiz et ve önemli öğelerin varlığını kontrol et
    """
    soup = BeautifulSoup(html_content, "html5lib")
    
    # Rapor dosyası için
    with open("debug/analysis.txt", "w", encoding="utf-8") as f:
        
        # Sayfa başlığını kontrol et
        title = soup.title.string if soup.title else "Başlık bulunamadı"
        f.write(f"Sayfa başlığı: {title}\n\n")
        
        # div.mt-4 öğeleri mevcut mu?
        mt4_divs = soup.select("div.mt-4")
        f.write(f"div.mt-4 öğe sayısı: {len(mt4_divs)}\n")
        
        # İlk div.mt-4 öğesinin içeriğini incele
        if mt4_divs:
            f.write("İlk div.mt-4 öğesinin içeriği:\n")
            f.write("-" * 50 + "\n")
            f.write(str(mt4_divs[0])[:1000] + "...\n\n")
            
            # h2 başlığı var mı?
            h2_tag = mt4_divs[0].find("h2")
            f.write(f"h2 başlığı bulundu mu: {h2_tag is not None}\n")
            if h2_tag:
                f.write(f"h2 içeriği: {h2_tag.text.strip()}\n\n")
                
            # Tablo var mı?
            table_tag = mt4_divs[0].find("table")
            f.write(f"Tablo bulundu mu: {table_tag is not None}\n")
            
            # Tablo satırları var mı?
            if table_tag:
                rows = table_tag.find_all("tr")
                f.write(f"Tablo satır sayısı: {len(rows)}\n\n")
                
                # İlk satırın yapısını incele
                if rows:
                    f.write("İlk satırın yapısı:\n")
                    f.write("-" * 50 + "\n")
                    f.write(str(rows[0])[:1000] + "...\n\n")
                    
                    # teams hücresi var mı?
                    teams_cell = rows[0].select_one("td.teams")
                    f.write(f"teams hücresi bulundu mu: {teams_cell is not None}\n")
                    if teams_cell:
                        f.write(f"teams hücresi içeriği: {teams_cell.text.strip()}\n\n")
        
        # HTML yapısındaki CSS sınıflarını raporla
        f.write("Sayfadaki CSS sınıfları:\n")
        f.write("-" * 50 + "\n")
        all_classes = set()
        for tag in soup.find_all(class_=True):
            for class_name in tag.get("class", []):
                all_classes.add(class_name)
        
        f.write(", ".join(sorted(all_classes)))
        
    print(f"HTML analizi tamamlandı: debug/analysis.txt")

if __name__ == "__main__":
    download_and_save_html() 
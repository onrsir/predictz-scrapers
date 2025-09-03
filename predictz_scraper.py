#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import datetime
import time
import os
import random
from typing import List, Dict, Any, Optional


class PredictzScraper:
    """
    Predictz.com sitesinden futbol maç tahminleri verilerini çeken scraper.
    Yarından başlayarak 4 günlük veri çeker.
    """
    
    def __init__(self):
        self.base_url = "https://www.predictz.com/predictions/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.output_folder = "data"
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        # 4 günlük tarih listesi oluştur (yarın + sonraki 3 gün)
        self.dates_to_scrape = self.generate_date_list()
    
    def generate_date_list(self) -> List[str]:
        """
        Yarından başlayarak 4 günlük tarih listesi oluştur
        Format: 20250825 formatında
        """
        dates = []
        today = datetime.datetime.now()
        
        # Yarından başla (i=1) ve 4 gün çek
        for i in range(1, 5):
            date = today + datetime.timedelta(days=i)
            dates.append(date.strftime("%Y%m%d"))
        
        print(f"Çekilecek tarihler: {', '.join(dates)}")
        return dates
    
    def get_page_content(self, date_str: str) -> Optional[str]:
        """
        Belirli bir tarih için web sayfasını indir ve HTML içeriğini döndür
        
        Args:
            date_str (str): YYYYMMDD formatında tarih
        
        Returns:
            Optional[str]: HTML içeriği veya None
        """
        url = f"{self.base_url}{date_str}/"
        
        try:
            print(f"Tarih {date_str} için veri çekiliyor: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Hata: {date_str} tarihli sayfa içeriği alınamadı - {e}")
            return None
    
    def parse_page(self, html_content: str, date_str: str) -> List[Dict[str, Any]]:
        """
        HTML içeriğini ayrıştır ve maç tahminlerini çıkar
        
        Args:
            html_content (str): HTML içeriği
            date_str (str): YYYYMMDD formatında tarih
        
        Returns:
            List[Dict[str, Any]]: Lig ve maç verilerini içeren liste
        """
        soup = BeautifulSoup(html_content, "html5lib")
        leagues_data = []
        
        # Ana tabloyu bul
        table_div = soup.select_one("div.pttable")
        if not table_div:
            print(f"Tarih {date_str} için maç tablosu bulunamadı!")
            return []
        
        # Lig başlıkları ve maç satırlarını bul
        rows = table_div.find_all(class_=["pttrnh ptttl", "pttr ptcnt"])
        
        current_league = None
        current_league_data = None
        
        for row in rows:
            # Lig başlığı satırı
            if "pttrnh" in row.get("class", []) and "ptttl" in row.get("class", []):
                league_header = row.select_one("h2")
                if league_header:
                    current_league = league_header.text.strip()
                    current_league_data = {
                        "league_name": current_league,
                        "matches": []
                    }
                    leagues_data.append(current_league_data)
            
            # Maç satırı
            elif "pttr" in row.get("class", []) and "ptcnt" in row.get("class", []) and current_league_data:
                # Takımları içeren hücreyi bul
                game_cell = row.select_one("div.pttd.ptgame")
                if not game_cell or " v " not in game_cell.text:
                    continue
                
                # Takımları ayır
                teams_text = game_cell.text.strip()
                home_team, away_team = teams_text.split(" v ")
                
                # Tahmin kutusunu bul
                prediction_cell = row.select_one("div.pttd.ptprd div")
                score_prediction = prediction_cell.text.strip() if prediction_cell else None
                
                match_data = {
                    "home_team": home_team.strip(),
                    "away_team": away_team.strip(),
                    "prediction": score_prediction,
                    "match_date": date_str
                }
                
                current_league_data["matches"].append(match_data)
        
        return leagues_data
    
    def save_to_json(self, data: List[Dict[str, Any]], date_str: str) -> str:
        """
        Veriyi JSON formatında kaydet
        
        Args:
            data (List[Dict[str, Any]]): Kaydedilecek veri
            date_str (str): YYYYMMDD formatında tarih
        
        Returns:
            str: Kaydedilen dosya adı
        """
        # YYYYMMDD formatını YYYY-MM-DD formatına çevir
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        filename = f"{self.output_folder}/predictz_data_{formatted_date}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return filename
    
    def save_combined_data(self, all_data: Dict[str, Any]) -> str:
        """
        Tüm günlerin verilerini tek bir dosyada birleştir
        
        Args:
            all_data (Dict[str, Any]): Tüm günlerin verileri
        
        Returns:
            str: Kaydedilen dosya adı
        """
        # Çekilen tarihlerin en erken tarihini al
        dates_scraped = all_data.get("dates_scraped", [])
        if dates_scraped:
            # İlk tarihi kullan (YYYYMMDD -> YYYY-MM-DD)
            first_date = dates_scraped[0]
            formatted_date = f"{first_date[:4]}-{first_date[4:6]}-{first_date[6:8]}"
        else:
            # Fallback: bugünün tarihi
            formatted_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        filename = f"{self.output_folder}/predictz_combined_{formatted_date}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        
        return filename
    
    def run(self) -> None:
        """
        Scraper'ı çalıştır - 4 günlük veri çeker
        """
        print("Predictz.com yarından başlayarak 4 günlük verilerini çekme işlemi başlatılıyor...")
        
        all_data = {
            "scrape_timestamp": datetime.datetime.now().isoformat(),
            "dates_scraped": self.dates_to_scrape,
            "data_by_date": {}
        }
        
        total_matches = 0
        successful_dates = 0
        
        for date_str in self.dates_to_scrape:
            print(f"\n{'='*50}")
            print(f"Tarih: {date_str} işleniyor...")
            print(f"{'='*50}")
            
            html_content = self.get_page_content(date_str)
            
            if not html_content:
                print(f"Tarih {date_str} için veri çekilemedi, atlanıyor.")
                continue
            
            parsed_data = self.parse_page(html_content, date_str)
            
            if not parsed_data:
                print(f"Tarih {date_str} için ayrıştırılabilir veri bulunamadı.")
                continue
            
            # Her tarihin verisini ayrı dosyaya kaydet
            saved_file = self.save_to_json(parsed_data, date_str)
            
            # Toplam veriyi birleştir (tarihi YYYY-MM-DD formatına çevir)
            formatted_date_key = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            all_data["data_by_date"][formatted_date_key] = parsed_data
            
            date_matches = sum(len(league['matches']) for league in parsed_data)
            total_matches += date_matches
            successful_dates += 1
            
            print(f"✅ Tarih {date_str}: {date_matches} maç, {len(parsed_data)} lig")
            print(f"📁 Kaydedildi: {saved_file}")
            
            # Bir sonraki tarihe geçmeden önce sıradaki tarihle devam edip etmeyeceğini kontrol et
            next_index = self.dates_to_scrape.index(date_str) + 1
            if next_index < len(self.dates_to_scrape):
                next_date = self.dates_to_scrape[next_index]
                print(f"⏳ Sonraki tarih ({next_date}) için 10 saniye bekleniyor...")
                for i in range(10, 0, -1):
                    print(f"\r⏱️  {i} saniye kaldı...", end="", flush=True)
                    time.sleep(1)
                print("\r✅ Bekleme tamamlandı!     ")
        
        if successful_dates > 0:
            # Birleştirilmiş veriyi kaydet
            combined_file = self.save_combined_data(all_data)
            
            print(f"\n🎉 İşlem tamamlandı!")
            print(f"📊 Özet:")
            print(f"   • Başarılı tarihler: {successful_dates}/{len(self.dates_to_scrape)}")
            print(f"   • Toplam maç sayısı: {total_matches}")
            print(f"   • Birleştirilmiş dosya: {combined_file}")
        else:
            print("❌ Hiçbir tarih için veri çekilemedi.")


if __name__ == "__main__":
    scraper = PredictzScraper()
    scraper.run() 
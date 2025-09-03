#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from predictz_scraper import PredictzScraper
import json
import os
from typing import Dict, Any

def display_match_details(match: Dict[str, Any]) -> None:
    """Bir maçın ayrıntılarını konsolda göster"""
    print(f"  🏠 {match['home_team']} vs ✈️ {match['away_team']}")
    
    if match.get("prediction"):
        print(f"  Skor Tahmini: {match['prediction']}")
    
    print()

def test_scraper() -> None:
    """Scraper'ı test et ve bazı sonuçları göster"""
    print("🔍 Predictz.com Scraper Test")
    print("=" * 50)
    
    # Scraper'ı başlat
    scraper = PredictzScraper()
    print("➡️ Veri çekiliyor...")
    
    # Verinin çekilip JSON'a kaydedilmesini sağla
    html_content = scraper.get_page_content()
    
    if not html_content:
        print("❌ HTML içeriği alınamadı!")
        return
        
    parsed_data = scraper.parse_page(html_content)
    
    if not parsed_data:
        print("❌ Veri ayrıştırılamadı!")
        return
        
    # Sonuçların bir kısmını konsola yazdır
    print(f"✅ Veri başarıyla çekildi! {len(parsed_data)} lig ve {sum(len(league['matches']) for league in parsed_data)} maç bulundu.\n")
    
    # İlk 2 ligden en fazla 3'er maç göster
    max_leagues = min(2, len(parsed_data))
    for i in range(max_leagues):
        league = parsed_data[i]
        print(f"🏆 {league['league_name']}")
        print("-" * 50)
        
        max_matches = min(3, len(league['matches']))
        for j in range(max_matches):
            if j < len(league['matches']):
                display_match_details(league['matches'][j])
            
    # JSON'a kaydet
    output_file = scraper.save_to_json(parsed_data)
    print(f"💾 Veriler JSON dosyasına kaydedildi: {output_file}")
    
    # Dosya boyutunu göster
    file_size = os.path.getsize(output_file) / 1024  # KB cinsinden
    print(f"📊 Dosya boyutu: {file_size:.2f} KB")

if __name__ == "__main__":
    test_scraper() 
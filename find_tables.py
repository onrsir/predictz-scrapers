#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

def find_league_tables():
    """
    HTML içerisindeki lig tablolarını ve yapılarını bul
    """
    url = "https://www.predictz.com/predictions/tomorrow/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print("Sayfa içeriği indiriliyor...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
        
        print("HTML içeriği ayrıştırılıyor...")
        soup = BeautifulSoup(html_content, "html5lib")
        
        # Önce contentfull sınıfına sahip div'leri bulalım
        content_divs = soup.select("div.contentfull")
        print(f"contentfull divlerin sayısı: {len(content_divs)}")
        
        # pttable sınıfına sahip div'leri bulalım
        table_divs = soup.select("div.pttable")
        print(f"pttable divlerin sayısı: {len(table_divs)}")
        
        if table_divs:
            # İlk tabloyu detaylı olarak inceleyelim
            first_table = table_divs[0]
            
            # Tablo başlıkları
            headers = first_table.select("div.pttrnh.ptttl")
            print(f"İlk tablodaki başlık sayısı: {len(headers)}")
            
            # Başlığın içeriğini görelim
            if headers:
                header = headers[0]
                header_text = header.text.strip()
                print(f"İlk başlık içeriği: {header_text[:100]}...")
                
                h2_tag = header.select_one("h2")
                if h2_tag:
                    print(f"Başlık içindeki h2: {h2_tag.text.strip()}")
            
            # Maç satırları
            match_rows = first_table.select("div.pttr.ptcnt")
            print(f"İlk tablodaki maç sayısı: {len(match_rows)}")
            
            # İlk maç satırını inceleyelim
            if match_rows:
                first_match = match_rows[0]
                
                # Takımları içeren hücre
                game_cell = first_match.select_one("div.pttd.ptgame")
                if game_cell:
                    game_text = game_cell.text.strip()
                    print(f"İlk maç: {game_text}")
                
                # Tahmin hücresi
                pred_cell = first_match.select_one("div.pttd.ptprd div")
                if pred_cell:
                    pred_text = pred_cell.text.strip()
                    pred_class = pred_cell.get("class", [])
                    print(f"Tahmin: {pred_text} (Sınıf: {pred_class})")
                
                # Form hücreleri
                form_cells = first_match.select("div.ptlast5boxh div, div.ptlast5wh div.last5box div")
                form_classes = [cell.get("class", []) for cell in form_cells]
                print(f"Form hücreleri sınıfları: {form_classes}")
                
                # Oran hücreleri
                odds_cells = first_match.select("div.pttd.ptodds")
                odds_values = [cell.text.strip() for cell in odds_cells]
                print(f"Oranlar: {odds_values}")
        
        else:
            print("Hiç pttable bulunamadı!")
            
            # Sayfa içindeki tüm div sınıflarını listeleyelim
            all_div_classes = set()
            for div in soup.find_all("div", class_=True):
                for class_name in div.get("class", []):
                    all_div_classes.add(class_name)
            
            print(f"Sayfadaki div sınıfları: {', '.join(sorted(all_div_classes))}")
            
            # İçeriğe daha derinlemesine bakalım
            content_element = soup.select_one("div#content")
            if content_element:
                print("Content div'i bulundu, direkt içeriklerini inceliyoruz...")
                
                # İlk birkaç çocuğuna bakalım
                children = list(content_element.children)[:5]
                for i, child in enumerate(children):
                    if hasattr(child, 'name'):
                        print(f"Child {i}: {child.name} - Class: {child.get('class', [])}")
                        if child.name == 'div' and hasattr(child, 'text'):
                            print(f"İçerik örneği: {child.text.strip()[:50]}...")
            
    except requests.RequestException as e:
        print(f"Hata: Web sayfası indirilemedi - {e}")
        return False

if __name__ == "__main__":
    find_league_tables() 
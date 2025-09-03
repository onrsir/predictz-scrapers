#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import datetime
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
import traceback

# Ana proje dizinini sys.path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Virtual environment aktivasyonu
venv_path = project_root / "venv"
if venv_path.exists():
    import site
    site_packages = venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    if site_packages.exists():
        site.addsitedir(str(site_packages))

# Scrapers'ları import et
from predictz_scraper import PredictzScraper


@dataclass
class ScrapingResult:
    """Scraping işlemi sonucu"""
    scraper_name: str
    success: bool
    data_file: Optional[str] = None
    error_message: Optional[str] = None
    total_matches: int = 0
    leagues_count: int = 0


@dataclass
class UploadResult:
    """Firebase upload işlemi sonucu"""
    success: bool
    uploaded_matches: int = 0
    skipped_matches: int = 0
    error_message: Optional[str] = None


class AutomationManager:
    """
    Scrapers ve Firebase upload otomasyonu yöneten ana sınıf
    """
    
    def __init__(self, config_file: str = "automation_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
        # Logging kurulumu
        self.setup_logging()
        
        # Paths
        self.scrapers_dir = Path(__file__).parent.parent
        self.predictor_dir = self.scrapers_dir.parent / "Predictor"
        self.upload_script = self.predictor_dir / "scripts" / "upload-predictz-matches.js"
        
        self.logger.info("AutomationManager başlatıldı")
    
    def load_config(self) -> Dict[str, Any]:
        """Configuration dosyasını yükle"""
        config_path = Path(__file__).parent / self.config_file
        
        if not config_path.exists():
            # Default config oluştur
            default_config = {
                "scrapers": {
                    "predictz": {
                        "enabled": True,
                        "class_name": "PredictzScraper",
                        "schedule": ["08:00", "20:00"]  # Günde 2 kez
                    }
                },
                "firebase": {
                    "auto_upload": True,
                    "delete_after_upload": False
                },
                "logging": {
                    "level": "INFO",
                    "max_file_size": "10MB",
                    "backup_count": 5
                },
                "notifications": {
                    "enabled": False,
                    "email": {
                        "smtp_server": "",
                        "port": 587,
                        "username": "",
                        "password": "",
                        "to_addresses": []
                    }
                }
            }
            
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            
            print(f"Default config oluşturuldu: {config_path}")
        
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def setup_logging(self):
        """Logging sistemini kur"""
        log_dir = Path(__file__).parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"automation_{datetime.datetime.now().strftime('%Y%m')}.log"
        
        logging.basicConfig(
            level=getattr(logging, self.config["logging"]["level"]),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def run_scraper(self, scraper_name: str) -> ScrapingResult:
        """Belirli bir scraper'ı çalıştır"""
        self.logger.info(f"{scraper_name} scraper'ı başlatılıyor...")
        
        try:
            if scraper_name == "predictz":
                scraper = PredictzScraper()
                scraper.run()
                
                # En son oluşturulan veri dosyasını bul (combined veya tek dosya)
                data_dir = self.scrapers_dir / "data"
                
                # Önce combined dosyaları ara
                combined_files = list(data_dir.glob("predictz_combined_*.json"))
                # Sonra tek dosyaları ara
                single_files = list(data_dir.glob("predictz_data_*.json"))
                
                # Tüm dosyaları birleştir ve en yenisini bul
                all_files = combined_files + single_files
                
                if not all_files:
                    return ScrapingResult(
                        scraper_name=scraper_name,
                        success=False,
                        error_message="Hiçbir predictz data dosyası bulunamadı"
                    )
                
                # En yeni dosyayı al (tarihe göre)
                def extract_date_from_filename(file_path):
                    """Dosya adından tarih çıkar (YYYY-MM-DD formatında)"""
                    import re
                    # predictz_combined_2025-09-05.json -> 2025-09-05
                    # predictz_data_2025-09-05.json -> 2025-09-05
                    match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path.name)
                    return match.group(1) if match else "1900-01-01"
                
                # En yeni tarihli dosyayı bul
                latest_file = max(all_files, key=extract_date_from_filename)
                latest_date = extract_date_from_filename(latest_file)
                self.logger.info(f"En yeni dosya bulundu: {latest_file.name} (tarih: {latest_date}, değişiklik zamanı: {datetime.datetime.fromtimestamp(latest_file.stat().st_mtime)})")
                
                # Eğer tek dosya ise, onu combined formatına dönüştür
                if latest_file.name.startswith("predictz_data_"):
                    self.logger.info(f"Tek dosya combined formatına dönüştürülüyor: {latest_file.name}")
                    latest_file = self.convert_single_to_combined(latest_file)
                else:
                    self.logger.info(f"Combined dosya kullanılıyor: {latest_file.name}")
                
                # Dosyadan istatistikleri çıkar
                with open(latest_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                total_matches = 0
                leagues_count = 0
                
                for date_data in data.get("data_by_date", {}).values():
                    leagues_count += len(date_data)
                    for league in date_data:
                        total_matches += len(league.get("matches", []))
                
                return ScrapingResult(
                    scraper_name=scraper_name,
                    success=True,
                    data_file=str(latest_file),
                    total_matches=total_matches,
                    leagues_count=leagues_count
                )
            
            else:
                return ScrapingResult(
                    scraper_name=scraper_name,
                    success=False,
                    error_message=f"Bilinmeyen scraper: {scraper_name}"
                )
                
        except Exception as e:
            self.logger.error(f"{scraper_name} scraper hatası: {str(e)}")
            return ScrapingResult(
                scraper_name=scraper_name,
                success=False,
                error_message=str(e)
            )
    
    def convert_single_to_combined(self, single_file: Path) -> Path:
        """Tek tarih dosyasını combined formatına dönüştür"""
        with open(single_file, "r", encoding="utf-8") as f:
            single_data = json.load(f)
        
        # Dosya adından tarihi çıkar (predictz_data_2025-08-29.json -> 2025-08-29)
        date_str = single_file.stem.split("_")[-1]
        
        # Veri formatını kontrol et ve doğru formata çevir
        if isinstance(single_data, list):
            # Eğer veri doğrudan list ise (yeni format)
            leagues_data = single_data
            generated_at = datetime.datetime.now().isoformat()
        elif isinstance(single_data, dict):
            # Eğer veri dict ise (eski format)
            leagues_data = single_data.get("leagues", [])
            generated_at = single_data.get("generated_at", datetime.datetime.now().isoformat())
        else:
            # Beklenmeyen format
            self.logger.error(f"Beklenmeyen dosya formatı: {single_file}")
            raise ValueError(f"Desteklenmeyen veri formatı: {type(single_data)}")
        
        # Combined format oluştur
        combined_data = {
            "scraper": "predictz",
            "generated_at": generated_at,
            "data_by_date": {
                date_str: leagues_data
            }
        }
        
        # Combined dosya adı
        combined_file = single_file.parent / f"predictz_combined_{date_str}.json"
        
        # Combined dosyayı kaydet
        with open(combined_file, "w", encoding="utf-8") as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Tek dosya combined formatına dönüştürüldü: {combined_file}")
        return combined_file
    
    def convert_combined_to_upload_format(self, combined_file: str) -> str:
        """Combined JSON formatını upload script'inin beklediği formata dönüştür"""
        with open(combined_file, "r", encoding="utf-8") as f:
            combined_data = json.load(f)
        
        # Her tarih için ayrı dosya oluştur ve upload et
        upload_results = []
        
        for date_str, leagues_data in combined_data.get("data_by_date", {}).items():
            # Upload formatına dönüştür (sadece leagues array'i)
            upload_data = leagues_data  # Bu zaten doğru format
            
            # Geçici upload dosyası oluştur
            temp_file = Path(combined_file).parent / f"temp_upload_{date_str}.json"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(upload_data, f, ensure_ascii=False, indent=2)
            
            upload_results.append((str(temp_file), date_str))
        
        return upload_results
    
    def upload_to_firebase(self, data_file: str) -> UploadResult:
        """Veriyi Firebase'e upload et"""
        self.logger.info(f"Firebase upload başlatılıyor: {data_file}")
        
        try:
            # Combined dosyayı upload formatına dönüştür
            upload_files = self.convert_combined_to_upload_format(data_file)
            
            total_uploaded = 0
            total_skipped = 0
            
            # Her tarihi ayrı ayrı upload et
            for temp_file, date_str in upload_files:
                self.logger.info(f"Tarih {date_str} için upload başlatılıyor...")
                
                try:
                    # Node.js script'ini çalıştır
                    cmd = ["node", str(self.upload_script), temp_file]
                    
                    result = subprocess.run(
                        cmd,
                        cwd=str(self.predictor_dir),
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 dakika timeout
                    )
                    
                    if result.returncode == 0:
                        # Output'tan başarı bilgilerini çıkar
                        output_lines = result.stdout.strip().split('\n')
                        
                        for line in output_lines:
                            if "Başarılı:" in line:
                                try:
                                    uploaded = int(line.split("Başarılı:")[-1].strip())
                                    total_uploaded += uploaded
                                except:
                                    pass
                            elif "Atlanan:" in line:
                                try:
                                    skipped = int(line.split("Atlanan:")[-1].strip())
                                    total_skipped += skipped
                                except:
                                    pass
                        
                        self.logger.info(f"Tarih {date_str} upload tamamlandı")
                    else:
                        error_msg = result.stderr or result.stdout
                        self.logger.error(f"Tarih {date_str} upload hatası: {error_msg}")
                        raise Exception(f"Upload failed for {date_str}: {error_msg}")
                    
                finally:
                    # Geçici dosyayı temizle
                    try:
                        os.remove(temp_file)
                    except:
                        pass
            
            self.logger.info(f"Tüm tarihler için Firebase upload başarılı: {total_uploaded} yüklendi, {total_skipped} atlandı")
            
            return UploadResult(
                success=True,
                uploaded_matches=total_uploaded,
                skipped_matches=total_skipped
            )
                
        except subprocess.TimeoutExpired:
            error_msg = "Firebase upload timeout (5 dakika)"
            self.logger.error(error_msg)
            return UploadResult(success=False, error_message=error_msg)
            
        except Exception as e:
            error_msg = f"Firebase upload exception: {str(e)}"
            self.logger.error(error_msg)
            return UploadResult(success=False, error_message=error_msg)
    
    def send_notification(self, subject: str, message: str):
        """Bildirim gönder"""
        if not self.config["notifications"]["enabled"]:
            return
        
        # Şimdilik sadece log'a yaz, ileride email/slack eklenebilir
        self.logger.info(f"NOTIFICATION - {subject}: {message}")
    
    def run_automation(self, scraper_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Tam otomasyon döngüsünü çalıştır"""
        start_time = datetime.datetime.now()
        
        self.logger.info("Otomasyon döngüsü başlatılıyor...")
        
        if scraper_names is None:
            # Aktif scrapers'ları belirle
            scraper_names = [
                name for name, config in self.config["scrapers"].items() 
                if config.get("enabled", False)
            ]
        
        results = {
            "start_time": start_time.isoformat(),
            "scrapers": {},
            "uploads": {},
            "summary": {
                "total_scrapers": len(scraper_names),
                "successful_scrapers": 0,
                "failed_scrapers": 0,
                "total_matches_scraped": 0,
                "total_matches_uploaded": 0,
                "total_matches_skipped": 0
            }
        }
        
        # Her scraper'ı çalıştır
        for scraper_name in scraper_names:
            self.logger.info(f"=== {scraper_name.upper()} SCRAPER ===")
            
            # Scraping yap
            scraping_result = self.run_scraper(scraper_name)
            results["scrapers"][scraper_name] = scraping_result.__dict__
            
            if scraping_result.success:
                results["summary"]["successful_scrapers"] += 1
                results["summary"]["total_matches_scraped"] += scraping_result.total_matches
                
                self.logger.info(f"{scraper_name}: {scraping_result.total_matches} maç, {scraping_result.leagues_count} lig")
                
                # Firebase upload
                if self.config["firebase"]["auto_upload"] and scraping_result.data_file:
                    self.logger.info(f"=== {scraper_name.upper()} FIREBASE UPLOAD ===")
                    
                    upload_result = self.upload_to_firebase(scraping_result.data_file)
                    results["uploads"][scraper_name] = upload_result.__dict__
                    
                    if upload_result.success:
                        results["summary"]["total_matches_uploaded"] += upload_result.uploaded_matches
                        results["summary"]["total_matches_skipped"] += upload_result.skipped_matches
                        
                        # Başarılı upload sonrası dosyayı sil (opsiyonel)
                        if self.config["firebase"]["delete_after_upload"]:
                            try:
                                os.remove(scraping_result.data_file)
                                self.logger.info(f"Upload sonrası dosya silindi: {scraping_result.data_file}")
                            except Exception as e:
                                self.logger.warning(f"Dosya silinemedi: {e}")
                    else:
                        self.send_notification(
                            f"{scraper_name} Upload Hatası",
                            f"Firebase upload başarısız: {upload_result.error_message}"
                        )
                
            else:
                results["summary"]["failed_scrapers"] += 1
                self.send_notification(
                    f"{scraper_name} Scraper Hatası", 
                    f"Scraping başarısız: {scraping_result.error_message}"
                )
        
        # Sonuçları kaydet
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        results["end_time"] = end_time.isoformat()
        results["duration_seconds"] = duration
        
        # Sonuçları dosyaya kaydet
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        results_file = results_dir / f"automation_result_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        # Özet log
        summary = results["summary"]
        self.logger.info("=== OTOMASYON ÖZETİ ===")
        self.logger.info(f"Süre: {duration:.1f} saniye")
        self.logger.info(f"Scrapers: {summary['successful_scrapers']}/{summary['total_scrapers']} başarılı")
        self.logger.info(f"Toplam scrape edilen maç: {summary['total_matches_scraped']}")
        self.logger.info(f"Firebase'e yüklenen maç: {summary['total_matches_uploaded']}")
        self.logger.info(f"Atlanan maç: {summary['total_matches_skipped']}")
        self.logger.info(f"Sonuç dosyası: {results_file}")
        
        return results


def main():
    """Ana fonksiyon - komut satırından çalıştırmak için"""
    if len(sys.argv) > 1:
        # Belirli scrapers çalıştır
        scrapers = sys.argv[1].split(',')
    else:
        # Tüm aktif scrapers'ları çalıştır
        scrapers = None
    
    try:
        manager = AutomationManager()
        results = manager.run_automation(scrapers)
        
        # Exit code
        if results["summary"]["failed_scrapers"] == 0:
            sys.exit(0)  # Başarılı
        else:
            sys.exit(1)  # Hata var
            
    except Exception as e:
        logging.error(f"Kritik hata: {str(e)}")
        logging.error(traceback.format_exc())
        sys.exit(2)


if __name__ == "__main__":
    main()

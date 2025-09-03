#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import schedule
import time
import datetime
from pathlib import Path
import sys
import logging

# Ana proje dizinini sys.path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from automation.automation_manager import AutomationManager

# Logging kurulumu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class CloudScheduler:
    """
    Cloud ortamında çalışan scheduler
    """
    
    def __init__(self):
        self.manager = AutomationManager()
        logger.info("CloudScheduler başlatıldı")
    
    def run_automation_job(self):
        """Automation job'ını çalıştır"""
        try:
            logger.info("⏰ Zamanlanmış automation job başlatılıyor...")
            
            # Automation'ı çalıştır
            results = self.manager.run_automation(['predictz'])
            
            # Sonuçları logla
            summary = results.get('summary', {})
            logger.info(f"✅ Automation tamamlandı: {summary.get('successful_scrapers', 0)}/{summary.get('total_scrapers', 0)} başarılı")
            logger.info(f"📊 Maçlar: {summary.get('total_matches_scraped', 0)} scrape, {summary.get('total_matches_uploaded', 0)} upload")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Automation job hatası: {str(e)}")
            return False
    
    def start_scheduler(self):
        """Scheduler'ı başlat"""
        logger.info("🚀 Cloud scheduler başlatılıyor...")
        
        # Schedule tanımla (UTC saatleri)
        schedule.every().day.at("05:00").do(self.run_automation_job)  # 08:00 Türkiye saati
        schedule.every().day.at("17:00").do(self.run_automation_job)  # 20:00 Türkiye saati
        
        logger.info("⏰ Schedule kuruldu: 05:00 UTC (08:00 TR) ve 17:00 UTC (20:00 TR)")
        
        # İlk çalıştırmayı hemen yap (test için)
        logger.info("🧪 İlk test çalıştırması yapılıyor...")
        self.run_automation_job()
        
        # Ana döngü
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Her dakika kontrol et
                
                # Her saat log ver (hayatta olduğunu göster)
                current_time = datetime.datetime.now()
                if current_time.minute == 0:
                    logger.info(f"💓 Scheduler çalışıyor - {current_time.strftime('%H:%M UTC')}")
                    
            except KeyboardInterrupt:
                logger.info("👋 Scheduler kapatılıyor...")
                break
            except Exception as e:
                logger.error(f"⚠️ Scheduler hatası: {str(e)}")
                time.sleep(300)  # 5 dakika bekle ve devam et


async def health_check_server():
    """Health check endpoint için basit HTTP server"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import threading
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'OK')
            else:
                self.send_response(404)
                self.end_headers()
        
        def log_message(self, format, *args):
            pass  # Sessiz mod
    
    def run_server():
        server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
        server.serve_forever()
    
    # Health check server'ı arka planda çalıştır
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    logger.info("🏥 Health check server başlatıldı: http://0.0.0.0:8080/health")


def main():
    """Ana fonksiyon"""
    try:
        # Health check server'ı başlat (cloud platformlar için)
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(health_check_server())
        
        # Scheduler'ı başlat
        scheduler = CloudScheduler()
        scheduler.start_scheduler()
        
    except Exception as e:
        logger.error(f"💥 Kritik hata: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

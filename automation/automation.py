#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import subprocess
from pathlib import Path


def main():
    """Ana automation komut arayüzü"""
    
    parser = argparse.ArgumentParser(
        description="İddia Meselesi Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Kullanım Örnekleri:
  %(prog)s run                    # Tüm scrapers'ları çalıştır
  %(prog)s run predictz           # Sadece predictz scraper'ını çalıştır  
  %(prog)s schedule install       # Cron job'ları kur
  %(prog)s schedule list          # Aktif cron job'ları listele
  %(prog)s schedule remove        # Cron job'ları kaldır
  %(prog)s monitor                # Web dashboard'unu başlat
  %(prog)s test predictz          # Test çalıştırması yap

Otomasyon Kurulumu:
  1. %(prog)s run                 # İlk test çalıştırması
  2. %(prog)s schedule install    # Otomatik çalıştırmayı etkinleştir
  3. %(prog)s monitor             # İzleme dashboard'unu başlat
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Komutlar")
    
    # RUN komutu
    run_parser = subparsers.add_parser("run", help="Scrapers'ları çalıştır")
    run_parser.add_argument("scrapers", nargs="*", help="Çalıştırılacak scraper adları (boş ise tümü)")
    
    # SCHEDULE komutu
    schedule_parser = subparsers.add_parser("schedule", help="Cron job yönetimi")
    schedule_subparsers = schedule_parser.add_subparsers(dest="schedule_action")
    
    schedule_subparsers.add_parser("install", help="Cron job'ları kur")
    schedule_subparsers.add_parser("remove", help="Cron job'ları kaldır")
    schedule_subparsers.add_parser("list", help="Cron job'ları listele")
    
    # TEST komutu
    test_parser = subparsers.add_parser("test", help="Test çalıştırması")
    test_parser.add_argument("scraper", nargs="?", help="Test edilecek scraper")
    
    # MONITOR komutu
    monitor_parser = subparsers.add_parser("monitor", help="Web dashboard'unu başlat")
    monitor_parser.add_argument("--port", "-p", type=int, default=8080, help="Port numarası")
    monitor_parser.add_argument("--no-browser", action="store_true", help="Tarayıcıyı açma")
    
    # CONFIG komutu
    config_parser = subparsers.add_parser("config", help="Konfigürasyon görüntüle")
    
    # STATUS komutu
    status_parser = subparsers.add_parser("status", help="Sistem durumunu göster")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    automation_dir = Path(__file__).parent
    
    try:
        if args.command == "run":
            # Automation manager'ı çalıştır
            venv_python = automation_dir.parent / "venv" / "bin" / "python3"
            python_cmd = str(venv_python) if venv_python.exists() else "python3"
            
            cmd = [python_cmd, str(automation_dir / "automation_manager.py")]
            if args.scrapers:
                cmd.append(",".join(args.scrapers))
            
            subprocess.run(cmd, cwd=str(automation_dir))
        
        elif args.command == "schedule":
            # Scheduler'ı çalıştır
            venv_python = automation_dir.parent / "venv" / "bin" / "python3"
            python_cmd = str(venv_python) if venv_python.exists() else "python3"
            
            cmd = [python_cmd, str(automation_dir / "scheduler.py"), args.schedule_action]
            subprocess.run(cmd, cwd=str(automation_dir))
        
        elif args.command == "test":
            # Test çalıştırması
            venv_python = automation_dir.parent / "venv" / "bin" / "python3"
            python_cmd = str(venv_python) if venv_python.exists() else "python3"
            
            cmd = [python_cmd, str(automation_dir / "scheduler.py"), "test"]
            if args.scraper:
                cmd.extend(["--scraper", args.scraper])
            
            subprocess.run(cmd, cwd=str(automation_dir))
        
        elif args.command == "monitor":
            # Dashboard'u başlat
            venv_python = automation_dir.parent / "venv" / "bin" / "python3"
            python_cmd = str(venv_python) if venv_python.exists() else "python3"
            
            cmd = [python_cmd, str(automation_dir / "monitor_dashboard.py"), "--port", str(args.port)]
            if args.no_browser:
                cmd.append("--no-browser")
            
            subprocess.run(cmd, cwd=str(automation_dir))
        
        elif args.command == "config":
            # Config dosyasını göster
            config_file = automation_dir / "automation_config.json"
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    import json
                    config = json.load(f)
                    print(json.dumps(config, indent=2, ensure_ascii=False))
            else:
                print("Config dosyası bulunamadı. İlk çalıştırmayı yapın.")
        
        elif args.command == "status":
            # Sistem durumunu göster
            show_status(automation_dir)
    
    except KeyboardInterrupt:
        print("\n👋 İşlem iptal edildi")
    except Exception as e:
        print(f"❌ Hata: {e}")
        sys.exit(1)


def show_status(automation_dir: Path):
    """Sistem durumunu göster"""
    import json
    import datetime
    
    print("🎯 İddia Meselesi Automation System Durumu")
    print("=" * 50)
    
    # Config durumu
    config_file = automation_dir / "automation_config.json"
    if config_file.exists():
        print("✅ Config dosyası: Mevcut")
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            
        enabled_scrapers = [name for name, cfg in config.get("scrapers", {}).items() if cfg.get("enabled")]
        print(f"📊 Aktif scrapers: {', '.join(enabled_scrapers) if enabled_scrapers else 'Yok'}")
        print(f"🔄 Otomatik upload: {'Evet' if config.get('firebase', {}).get('auto_upload') else 'Hayır'}")
    else:
        print("❌ Config dosyası: Bulunamadı")
    
    # Son çalıştırma durumu
    results_dir = automation_dir / "results"
    if results_dir.exists():
        result_files = list(results_dir.glob("automation_result_*.json"))
        if result_files:
            latest_result = max(result_files, key=lambda f: f.stat().st_mtime)
            print(f"📅 Son çalıştırma: {latest_result.name}")
            
            with open(latest_result, "r", encoding="utf-8") as f:
                result = json.load(f)
                summary = result.get("summary", {})
                print(f"📈 Son durum: {summary.get('successful_scrapers', 0)}/{summary.get('total_scrapers', 0)} başarılı")
                print(f"⚡ Son süre: {result.get('duration_seconds', 0):.1f}s")
        else:
            print("📅 Son çalıştırma: Yok")
    else:
        print("📅 Son çalıştırma: Yok")
    
    # Cron job durumu
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if "İDDİA MESELESİ AUTOMATION" in result.stdout:
            job_count = result.stdout.count("* * *")  # Cron pattern'ları say
            print(f"⏰ Cron job'lar: {job_count} aktif")
        else:
            print("⏰ Cron job'lar: Kurulmamış")
    except:
        print("⏰ Cron job'lar: Kontrol edilemedi")
    
    # Log dosyası durumu
    logs_dir = automation_dir / "logs"
    if logs_dir.exists():
        log_files = list(logs_dir.glob("automation_*.log"))
        if log_files:
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            file_size = latest_log.stat().st_size / 1024  # KB
            print(f"📝 Log dosyası: {latest_log.name} ({file_size:.1f} KB)")
        else:
            print("📝 Log dosyası: Yok")
    else:
        print("📝 Log dosyası: Yok")
    
    print("\n💡 Yardım için: python automation.py --help")


if __name__ == "__main__":
    main()

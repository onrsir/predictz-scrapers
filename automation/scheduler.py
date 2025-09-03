#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import datetime
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import argparse


class CronScheduler:
    """
    Cron job'larını yöneten sınıf
    """
    
    def __init__(self):
        self.automation_script = Path(__file__).parent / "automation_manager.py"
        self.config_file = Path(__file__).parent / "automation_config.json"
        
    def load_config(self) -> Dict[str, Any]:
        """Config dosyasını yükle"""
        if not self.config_file.exists():
            print(f"Config dosyası bulunamadı: {self.config_file}")
            return {}
        
        with open(self.config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_current_crontab(self) -> str:
        """Mevcut crontab'ı al"""
        try:
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
            else:
                return ""
        except Exception:
            return ""
    
    def generate_cron_entries(self) -> List[str]:
        """Config'den cron entries oluştur"""
        config = self.load_config()
        entries = []
        
        # Comment header ekle
        entries.append("# === İDDİA MESELESİ AUTOMATION ===")
        
        for scraper_name, scraper_config in config.get("scrapers", {}).items():
            if not scraper_config.get("enabled", False):
                continue
                
            schedules = scraper_config.get("schedule", [])
            
            for schedule_time in schedules:
                # Schedule time format: "HH:MM"
                try:
                    hour, minute = schedule_time.split(":")
                    
                    # Cron format: minute hour * * * command  
                    venv_python = self.automation_script.parent.parent / "venv" / "bin" / "python3"
                    python_cmd = str(venv_python) if venv_python.exists() else "python3"
                    
                    cron_entry = f"{minute} {hour} * * * cd '{self.automation_script.parent}' && {python_cmd} '{self.automation_script}' {scraper_name} >> /tmp/automation.log 2>&1"
                    entries.append(cron_entry)
                    
                except ValueError:
                    print(f"Geçersiz schedule format: {schedule_time}")
        
        # Günlük log temizleme (her gece 02:00)
        cleanup_entry = f"0 2 * * * find '{self.automation_script.parent}/logs' -name '*.log' -mtime +30 -delete"
        entries.append(cleanup_entry)
        
        entries.append("# === END İDDİA MESELESİ AUTOMATION ===")
        
        return entries
    
    def install_cron_jobs(self) -> bool:
        """Cron job'ları sisteme yükle"""
        current_crontab = self.get_current_crontab()
        new_entries = self.generate_cron_entries()
        
        if not new_entries:
            print("Kurulacak cron job bulunamadı.")
            return False
        
        # Mevcut automation entries'i temizle
        lines = current_crontab.split('\n')
        filtered_lines = []
        skip_section = False
        
        for line in lines:
            if "=== İDDİA MESELESİ AUTOMATION ===" in line:
                skip_section = True
                continue
            elif "=== END İDDİA MESELESİ AUTOMATION ===" in line:
                skip_section = False
                continue
            elif not skip_section and line.strip():
                filtered_lines.append(line)
        
        # Yeni entries'i ekle
        new_crontab_lines = filtered_lines + new_entries
        new_crontab = '\n'.join(new_crontab_lines) + '\n'
        
        try:
            # Geçici dosyaya yaz
            temp_file = "/tmp/automation_crontab"
            with open(temp_file, "w") as f:
                f.write(new_crontab)
            
            # Crontab'ı yükle
            result = subprocess.run(["crontab", temp_file], capture_output=True, text=True)
            
            # Geçici dosyayı sil
            os.remove(temp_file)
            
            if result.returncode == 0:
                print("✅ Cron job'lar başarıyla yüklendi!")
                print("\nYüklenen job'lar:")
                for entry in new_entries:
                    if not entry.startswith("#"):
                        print(f"  {entry}")
                return True
            else:
                print(f"❌ Cron job yükleme hatası: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Cron job kurulum hatası: {e}")
            return False
    
    def remove_cron_jobs(self) -> bool:
        """Automation cron job'larını kaldır"""
        current_crontab = self.get_current_crontab()
        
        # Automation entries'i temizle
        lines = current_crontab.split('\n')
        filtered_lines = []
        skip_section = False
        removed_count = 0
        
        for line in lines:
            if "=== İDDİA MESELESİ AUTOMATION ===" in line:
                skip_section = True
                continue
            elif "=== END İDDİA MESELESİ AUTOMATION ===" in line:
                skip_section = False
                continue
            elif not skip_section:
                if line.strip():
                    filtered_lines.append(line)
            else:
                removed_count += 1
        
        if removed_count == 0:
            print("Kaldırılacak automation cron job bulunamadı.")
            return True
        
        try:
            # Yeni crontab'ı yükle
            new_crontab = '\n'.join(filtered_lines) + '\n'
            
            temp_file = "/tmp/automation_crontab"
            with open(temp_file, "w") as f:
                f.write(new_crontab)
            
            result = subprocess.run(["crontab", temp_file], capture_output=True, text=True)
            os.remove(temp_file)
            
            if result.returncode == 0:
                print(f"✅ {removed_count} cron job kaldırıldı!")
                return True
            else:
                print(f"❌ Cron job kaldırma hatası: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Cron job kaldırma hatası: {e}")
            return False
    
    def list_cron_jobs(self):
        """Mevcut automation cron job'larını listele"""
        current_crontab = self.get_current_crontab()
        lines = current_crontab.split('\n')
        
        in_automation_section = False
        automation_jobs = []
        
        for line in lines:
            if "=== İDDİA MESELESİ AUTOMATION ===" in line:
                in_automation_section = True
                continue
            elif "=== END İDDİA MESELESİ AUTOMATION ===" in line:
                in_automation_section = False
                continue
            elif in_automation_section and line.strip() and not line.startswith("#"):
                automation_jobs.append(line.strip())
        
        if automation_jobs:
            print("🕐 Aktif automation cron job'ları:")
            for i, job in enumerate(automation_jobs, 1):
                print(f"  {i}. {job}")
        else:
            print("Aktif automation cron job bulunamadı.")
    
    def test_run(self, scraper_name: str = None):
        """Test çalıştırması yap"""
        print(f"🧪 Test çalıştırması başlatılıyor...")
        
        venv_python = self.automation_script.parent.parent / "venv" / "bin" / "python3"
        python_cmd = str(venv_python) if venv_python.exists() else "python3"
        
        cmd = [python_cmd, str(self.automation_script)]
        if scraper_name:
            cmd.append(scraper_name)
        
        try:
            result = subprocess.run(cmd, cwd=str(self.automation_script.parent))
            
            if result.returncode == 0:
                print("✅ Test çalıştırması başarılı!")
            else:
                print(f"❌ Test çalıştırması başarısız! Exit code: {result.returncode}")
                
        except Exception as e:
            print(f"❌ Test çalıştırması hatası: {e}")


def main():
    parser = argparse.ArgumentParser(description="İddia Meselesi Automation Scheduler")
    parser.add_argument("action", choices=["install", "remove", "list", "test"], 
                       help="Yapılacak işlem")
    parser.add_argument("--scraper", "-s", help="Test için scraper adı")
    
    args = parser.parse_args()
    
    scheduler = CronScheduler()
    
    if args.action == "install":
        scheduler.install_cron_jobs()
    elif args.action == "remove":
        scheduler.remove_cron_jobs()
    elif args.action == "list":
        scheduler.list_cron_jobs()
    elif args.action == "test":
        scheduler.test_run(args.scraper)


if __name__ == "__main__":
    main()

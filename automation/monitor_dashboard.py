#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any
import http.server
import socketserver
from urllib.parse import parse_qs, urlparse
import webbrowser
import argparse


class MonitoringDashboard:
    """
    Basit web-based monitoring dashboard
    """
    
    def __init__(self):
        self.automation_dir = Path(__file__).parent
        self.results_dir = self.automation_dir / "results"
        self.logs_dir = self.automation_dir / "logs"
        
    def get_recent_results(self, limit: int = 10) -> List[Dict[str, Any]]:
        """En son automation sonuçlarını al"""
        if not self.results_dir.exists():
            return []
        
        result_files = list(self.results_dir.glob("automation_result_*.json"))
        result_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        results = []
        for file_path in result_files[:limit]:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["file_name"] = file_path.name
                    results.append(data)
            except Exception as e:
                print(f"Dosya okuma hatası {file_path}: {e}")
        
        return results
    
    def get_automation_stats(self, days: int = 7) -> Dict[str, Any]:
        """Automation istatistikleri"""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        
        results = self.get_recent_results(100)  # Son 100 sonuca bak
        
        # Tarih filtreleme
        filtered_results = []
        for result in results:
            try:
                result_date = datetime.datetime.fromisoformat(result["start_time"].replace("Z", "+00:00"))
                if result_date >= cutoff_date:
                    filtered_results.append(result)
            except:
                continue
        
        if not filtered_results:
            return {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "success_rate": 0,
                "total_matches_scraped": 0,
                "total_matches_uploaded": 0,
                "avg_duration": 0
            }
        
        total_runs = len(filtered_results)
        successful_runs = sum(1 for r in filtered_results if r["summary"]["failed_scrapers"] == 0)
        failed_runs = total_runs - successful_runs
        success_rate = (successful_runs / total_runs) * 100 if total_runs > 0 else 0
        
        total_matches_scraped = sum(r["summary"]["total_matches_scraped"] for r in filtered_results)
        total_matches_uploaded = sum(r["summary"]["total_matches_uploaded"] for r in filtered_results)
        
        durations = [r["duration_seconds"] for r in filtered_results if "duration_seconds" in r]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "success_rate": success_rate,
            "total_matches_scraped": total_matches_scraped,
            "total_matches_uploaded": total_matches_uploaded,
            "avg_duration": avg_duration
        }
    
    def get_recent_logs(self, limit: int = 50) -> List[str]:
        """Son log satırlarını al"""
        if not self.logs_dir.exists():
            return []
        
        # En son log dosyasını bul
        log_files = list(self.logs_dir.glob("automation_*.log"))
        if not log_files:
            return []
        
        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest_log, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return [line.strip() for line in lines[-limit:] if line.strip()]
        except:
            return []
    
    def generate_html(self) -> str:
        """HTML dashboard'unu oluştur"""
        results = self.get_recent_results(5)
        stats = self.get_automation_stats()
        logs = self.get_recent_logs(20)
        
        html = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>İddia Meselesi - Automation Monitor</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 1px;
        }}
        
        .success {{ color: #27ae60; }}
        .error {{ color: #e74c3c; }}
        .warning {{ color: #f39c12; }}
        .info {{ color: #3498db; }}
        
        .section {{
            background: white;
            margin-bottom: 30px;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .section h2 {{
            margin-bottom: 20px;
            color: #2c3e50;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }}
        
        .result-item {{
            border-left: 4px solid #ecf0f1;
            padding: 15px;
            margin-bottom: 10px;
            background: #f8f9fa;
        }}
        
        .result-success {{
            border-left-color: #27ae60;
        }}
        
        .result-error {{
            border-left-color: #e74c3c;
        }}
        
        .result-meta {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }}
        
        .logs {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            max-height: 400px;
            overflow-y: auto;
        }}
        
        .refresh-btn {{
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 20px;
        }}
        
        .refresh-btn:hover {{
            background: #2980b9;
        }}
        
        .last-updated {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
        }}
    </style>
    <script>
        function refreshPage() {{
            window.location.reload();
        }}
        
        // Auto refresh every 5 minutes
        setTimeout(function(){{
            window.location.reload();
        }}, 300000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 İddia Meselesi Automation Monitor</h1>
            <p>Son 7 günün automation istatistikleri ve durumu</p>
        </div>
        
        <button class="refresh-btn" onclick="refreshPage()">🔄 Yenile</button>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value success">{stats['total_runs']}</div>
                <div class="stat-label">Toplam Çalıştırma</div>
            </div>
            <div class="stat-card">
                <div class="stat-value {'success' if stats['success_rate'] > 80 else 'warning' if stats['success_rate'] > 50 else 'error'}">{stats['success_rate']:.1f}%</div>
                <div class="stat-label">Başarı Oranı</div>
            </div>
            <div class="stat-card">
                <div class="stat-value info">{stats['total_matches_scraped']}</div>
                <div class="stat-label">Toplam Scrape Edilen</div>
            </div>
            <div class="stat-card">
                <div class="stat-value success">{stats['total_matches_uploaded']}</div>
                <div class="stat-label">Firebase'e Yüklenen</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Son Çalıştırmalar</h2>
"""
        
        if results:
            for result in results:
                summary = result.get("summary", {})
                is_success = summary.get("failed_scrapers", 1) == 0
                status_class = "result-success" if is_success else "result-error"
                status_icon = "✅" if is_success else "❌"
                
                start_time = result.get("start_time", "")
                duration = result.get("duration_seconds", 0)
                
                html += f"""
            <div class="result-item {status_class}">
                <strong>{status_icon} {start_time[:19]}</strong>
                <div class="result-meta">
                    Süre: {duration:.1f}s | 
                    Scrapers: {summary.get('successful_scrapers', 0)}/{summary.get('total_scrapers', 0)} | 
                    Maçlar: {summary.get('total_matches_scraped', 0)} scrape, {summary.get('total_matches_uploaded', 0)} upload
                </div>
            </div>
"""
        else:
            html += "<p>Henüz çalıştırma kaydı bulunamadı.</p>"
        
        html += """
        </div>
        
        <div class="section">
            <h2>📝 Son Loglar</h2>
            <div class="logs">
"""
        
        if logs:
            for log in logs:
                html += f"{log}<br>"
        else:
            html += "Log bulunamadı."
        
        html += f"""
            </div>
        </div>
        
        <div class="last-updated">
            Son güncelleme: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
        return html


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler for the dashboard"""
    
    def __init__(self, *args, **kwargs):
        self.dashboard = MonitoringDashboard()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = self.dashboard.generate_html()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()


def main():
    parser = argparse.ArgumentParser(description="Automation Monitoring Dashboard")
    parser.add_argument("--port", "-p", type=int, default=8080, help="Port numarası")
    parser.add_argument("--no-browser", action="store_true", help="Tarayıcıyı otomatik açma")
    
    args = parser.parse_args()
    
    try:
        with socketserver.TCPServer(("", args.port), DashboardHandler) as httpd:
            print(f"🌐 Dashboard başlatıldı: http://localhost:{args.port}")
            print("Durdurmak için Ctrl+C tuşlayın")
            
            if not args.no_browser:
                webbrowser.open(f"http://localhost:{args.port}")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 Dashboard kapatıldı")
    except OSError as e:
        print(f"❌ Port {args.port} kullanılamıyor: {e}")
        print("Farklı bir port deneyin: python monitor_dashboard.py --port 8081")


if __name__ == "__main__":
    main()

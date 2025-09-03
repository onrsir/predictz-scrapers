# 🌐 Cloud Deployment Rehberi

PC kapalıyken de çalışması için cloud platformlarında deployment seçenekleri.

## 🆓 Seçenek 1: GitHub Actions (ÜCRETSİZ)

### Avantajlar:
- ✅ Tamamen ücretsiz (2000 dakika/ay)
- ✅ Kolay kurulum
- ✅ Git ile entegre
- ✅ Artifact desteği (loglar)

### Kurulum:
1. Projeyi GitHub'a push edin
2. Repository > Settings > Secrets and variables > Actions
3. Şu secrets'ları ekleyin:
   ```
   FIREBASE_API_KEY: AIzaSyDo48uGnrjDq5HAr04jMrX1ckAtYvTf-yE
   FIREBASE_AUTH_DOMAIN: predictor-b0025.firebaseapp.com
   FIREBASE_PROJECT_ID: predictor-b0025
   ```

### Çalışma şekli:
- Her gün 08:00 ve 20:00'da otomatik çalışır
- Hata durumunda email gönderir
- Logları 30 gün saklar

---

## 💰 Seçenek 2: Railway (~$5/ay)

### Avantajlar:
- ✅ Sürekli çalışan servis
- ✅ Otomatik restart
- ✅ Health check
- ✅ Kolay deployment

### Kurulum:
1. Railway.app'e kaydolun
2. GitHub repo'yu bağlayın
3. Environment variables ekleyin
4. Deploy edin

### Maliyeti:
- İlk $5 ücretsiz
- Sonrası ~$5-10/ay

---

## 🐳 Seçenek 3: Docker + VPS (~$5/ay)

### Avantajlar:
- ✅ Tam kontrol
- ✅ Düşük maliyet
- ✅ Scalable

### Kurulum:
```bash
# Docker build
docker build -t iddia-automation .

# Docker run
docker run -d \
  --name iddia-automation \
  --restart unless-stopped \
  -p 8080:8080 \
  -e FIREBASE_API_KEY="your-api-key" \
  -e FIREBASE_PROJECT_ID="predictor-b0025" \
  iddia-automation
```

---

## ☁️ Seçenek 4: AWS Lambda (Serverless)

### Avantajlar:
- ✅ Sadece kullanım başına ücret
- ✅ Otomatik scaling
- ✅ Çok düşük maliyet

### Kurulum:
1. AWS hesabı açın
2. Lambda function oluşturun
3. EventBridge ile trigger kurun
4. Deploy edin

---

## 🚀 Önerilen: GitHub Actions

**En pratik ve ücretsiz çözüm için GitHub Actions öneriyorum.**

### Hızlı başlangıç:

1. **Projeyi GitHub'a push edin**:
   ```bash
   cd /Users/onursir/Documents/iddia\ meselesi/
   git init
   git add .
   git commit -m "İddia Meselesi Automation System"
   git branch -M main
   git remote add origin https://github.com/USERNAME/iddia-meselesi.git
   git push -u origin main
   ```

2. **GitHub Secrets ekleyin**:
   - Repository Settings → Secrets and variables → Actions
   - `FIREBASE_API_KEY`, `FIREBASE_PROJECT_ID` ekleyin

3. **Workflow otomatik çalışacak**:
   - Her gün 08:00 ve 20:00'da
   - Actions tab'ından izleyebilirsiniz

### Monitoring:

- **GitHub Actions logs**: Gerçek zamanlı loglar
- **Email notifications**: Hata durumunda otomatik
- **Artifact downloads**: Log dosyalarını indirebilirsiniz

---

## 🔧 Troubleshooting

### GitHub Actions sorunları:
```bash
# Workflow'u manuel çalıştırma
Actions → İddia Meselesi Automation → Run workflow

# Logları kontrol etme  
Actions → Son çalıştırma → Job details
```

### Railway sorunları:
```bash
# Deployment logları
railway logs

# Servis durumu
railway status
```

### Docker sorunları:
```bash
# Container logları
docker logs iddia-automation

# Container'ı restart etme
docker restart iddia-automation
```

---

## 📊 Maliyet Karşılaştırması

| Platform | Aylık Maliyet | Avantajlar |
|----------|---------------|------------|
| GitHub Actions | **ÜCRETSİZ** | Kolay, güvenli |
| Railway | ~$5 | Sürekli çalışır |
| VPS + Docker | ~$5 | Tam kontrol |
| AWS Lambda | ~$1 | Çok ucuz |

**Sonuç**: GitHub Actions ile başlayın, ihtiyaca göre upgrade yapın!

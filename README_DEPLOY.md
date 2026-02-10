# Google Cloud VM Deployment Guide

## Gereksinimler
- Python 3.10+
- 4GB+ RAM (NLU modelleri için)
- İnternet erişimi (ilk model indirme için)

## Kurulum

### 1. Sistem Paketlerini Yükle
```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git
```

### 2. Proje Dosyalarını Kopyala
```bash
# Projeyi VM'e kopyala (scp, git clone, vb.)
sudo mkdir -p /opt/hicazybs
sudo cp -r . /opt/hicazybs/
cd /opt/hicazybs
```

### 3. Python Sanal Ortamı Oluştur
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Test Et (Manuel)
```bash
cd /opt/hicazybs
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```
Tarayıcıda `http://<VM_IP>:8000` adresini açın.

### 5. Systemd Servisi Kur (7/24 Çalışması İçin)
```bash
sudo cp deploy/hicazybs.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hicazybs
sudo systemctl start hicazybs
```

### 6. Servis Durumunu Kontrol Et
```bash
sudo systemctl status hicazybs
sudo journalctl -u hicazybs -f  # Canlı loglar
```

## Firewall (GCP)
GCP Console'da port 8000'i açın:
1. **VPC Network > Firewall** bölümüne gidin
2. Yeni kural ekleyin:
   - Direction: Ingress
   - Targets: All instances / Specific tag
   - Source IP ranges: `0.0.0.0/0`
   - Protocols and ports: `tcp:8000`

## Güncelleme
```bash
cd /opt/hicazybs
# Yeni dosyaları kopyala
sudo systemctl restart hicazybs
```

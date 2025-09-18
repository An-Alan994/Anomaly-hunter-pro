# ⚡ Anomaly Hunter Pro
Trading bot kuantitatif hybrid untuk mendeteksi anomali market dan eksekusi otomatis di KuCoin.

---

## 🚀 Features
- Multi-provider (KuCoin, CoinGecko, Messari)
- Redundancy check harga
- Risk management (position sizing, exposure limit)
- Structured logging
- Database SQLite
- Docker + CI/CD pipeline
- Telegram deployment notifications

---

## 📦 Install & Run (Dev)
```bash
git clone https://github.com/youruser/anomaly_hunter_pro.git
cd anomaly_hunter_pro
cp .env.example .env
docker compose up --build

# Anomaly Hunter Pro

## Fitur Utama
- Deteksi coin hijau di lautan merah (anomaly hunter)
- Output Telegram edukatif multi-thread ("ANOMALY LAYAK BATTLE")
- Risk Management otomatis (position size, stop-loss)
- Redundancy data provider (CoinGecko, KuCoin, CryptoPanic)
- Logging ke database

## Instalasi di Termux
```bash
pkg update
pkg install python
pip install --upgrade pip
pip install -r requirements.txt
```

## Setup API & Environment
Salin `.env.example` ke `.env`, isi dengan API key Anda.

## Cara Jalankan
```bash
python main.py
```

## Output Telegram Contoh
> 🚨 RNDR | Skor: 85/100 | LONG | Entry: $7.70 | SL: $6.90 | R/R: 1:3
> ⛏️ Anomali: BTC turun -5%, RNDR hijau +12%.
> 🔍 Net Flow: -$12M, New Addresses +22%, RSI Oversold.
> 💡 Catalyst: Kerjasama Apple Vision Pro
> ⚔️ Risk: Size max 2% equity, loss max $210

## Lisensi
Lihat LICENSE untuk detail hak pakai.

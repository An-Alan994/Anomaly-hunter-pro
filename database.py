import sqlite3
import time

class DatabaseManager:
    """Manajer operasi database SQLite untuk menyimpan sinyal dan trades"""
    
    def __init__(self, db_name="trading_bot.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Inisialisasi tabel database"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Tabel sinyal
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    signal_type TEXT NOT NULL,
                    confidence REAL,
                    timestamp REAL NOT NULL,
                    source TEXT NOT NULL
                )
            ''')
            
            # Tabel pemeriksaan harga
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price1 REAL NOT NULL,
                    price2 REAL NOT NULL,
                    diff_percent REAL NOT NULL,
                    status TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            ''')
            
            conn.commit()
    
    def log_signal(self, symbol, price, signal_type, confidence, source):
        """Log sinyal trading ke database"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO signals (symbol, price, signal_type, confidence, timestamp, source)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (symbol, price, signal_type, confidence, time.time(), source))
            conn.commit()
    
    def log_price_check(self, symbol, price1, price2, diff_percent, status):
        """Log hasil perbandingan harga"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO price_checks (symbol, price1, price2, diff_percent, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (symbol, price1, price2, diff_percent, status, time.time()))
            conn.commit()

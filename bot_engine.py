import time
import logging
from providers import CoinGeckoProvider, KucoinProvider
from redundancy import RedundancyManager
from database import DatabaseManager

class AnomalyHunterBot:
    """Main class trading bot dengan verifikasi data multi-sumber"""
    
    def __init__(self):
        self.coingecko = CoinGeckoProvider()
        self.kucoin = KucoinProvider()
        self.redundancy = RedundancyManager()
        self.db = DatabaseManager()
        
        # Setup logging dasar
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def fetch_market_data(self, symbol="BTC"):
        """
        Ambil data market dari multiple sources dengan redundancy check
        Mengembalikan: data market terkonsolidasi atau None jika discrepancy terlalu tinggi
        """
        # Ambil data dari kedua provider
        cg_data = self.coingecko.get_price(symbol.lower(), "usd")
        kc_data = self.kucoin.get_price(f"{symbol}-USDT")
        
        # Cek error
        if "error" in cg_data:
            self.logger.error(f"CoinGecko error: {cg_data['error']}")
        if "error" in kc_data:
            self.logger.error(f"KuCoin error: {kc_data['error']}")
        
        # Bandingkan harga
        comparison = self.redundancy.check_price_discrepancy(cg_data, kc_data, tolerance=0.01)
        
        # Log hasil perbandingan
        self.db.log_price_check(
            symbol=symbol,
            price1=comparison.get("price1", 0),
            price2=comparison.get("price2", 0),
            diff_percent=comparison.get("diff_percent", 0),
            status=comparison.get("status", "error")
        )
        
        if comparison["status"] == "OK":
            return {
                "symbol": symbol,
                "price": comparison["avg_price"],
                "timestamp": time.time(),
                "source": "consolidated"
            }
        else:
            self.logger.warning(
                f"Price discrepancy detected: {comparison['diff_percent']}% "
                f"for {symbol}"
            )
            return None
    
    def run_single_iteration(self):
        """Eksekusi satu siklus lengkap pengecekan data"""
        self.logger.info("Starting market data check...")
        
        # Cek multiple cryptocurrency utama
        symbols = ["BTC", "ETH", "SOL", "BNB"]
        
        for symbol in symbols:
            market_data = self.fetch_market_data(symbol)
            
            if market_data:
                self.logger.info(
                    f"{symbol}: ${market_data['price']:.2f} "
                    f"(consolidated from multiple sources)"
                )
                
                # Di sini nanti ditambahkan logika anomaly detection
                # Untuk sekarang, hanya log successful data retrieval
                
            time.sleep(1)  # Hormati rate limits
        
        self.logger.info("Market data check completed")

from providers.kucoin_provider import KucoinProvider
from core.redundancy import RedundancyManager
from core.risk_manager import RiskManager
from data.database import DatabaseManager
from utils.logger import StructuredLogger

logger = StructuredLogger()
db = DatabaseManager()
kucoin = KucoinProvider()
risk = RiskManager()
redundancy = RedundancyManager()

def run():
    price = kucoin.get_price("BTC-USDT")
    ok, outlier = redundancy.check_price_discrepancy({"kucoin": price})
    if not ok:
        logger.log_trade_signal({"msg": f"Outlier detected from {outlier}"})
        return

    size = risk.calculate_position_size()
    # Simulasi trade
    logger.log_trade_signal({"symbol": "BTC-USDT", "side": "buy", "price": price, "size": size})
    with db.get_connection() as conn:
        conn.execute("INSERT INTO trades(symbol, side, price, size) VALUES (?, ?, ?, ?)",
                     ("BTC-USDT", "buy", price, size))
        conn.commit()

if __name__ == "__main__":
    run()

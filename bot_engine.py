import time
import logging
from typing import Dict
from providers import CoinGeckoProvider, KucoinProvider, CryptoPanicProvider
from redundancy import RedundancyManager
from database import DatabaseManager
from anomaly_detector import AnomalyDetector
from risk_manager import RiskManager
from telegram_notifier import TelegramNotifier

class AnomalyHunterBot:
    def __init__(self):
        self.coingecko = CoinGeckoProvider()
        self.kucoin = KucoinProvider()
        self.cryptopanic = CryptoPanicProvider()
        self.redundancy = RedundancyManager()
        self.detector = AnomalyDetector()
        self.risk_manager = RiskManager()
        self.db = DatabaseManager()
        self.telegram = TelegramNotifier()
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.tracked_symbols = [
            "bitcoin", "ethereum", "solana", "binancecoin", "cardano",
            "polkadot", "chainlink", "avalanche-2", "cosmos", "matic-network"
        ]
        self.min_confidence = 60
    
    def fetch_market_data(self) -> Dict:
        consolidated_data = {}
        gecko_data = self.coingecko.get_market_data(self.tracked_symbols, "usd")
        if "error" not in gecko_data:
            for symbol in self.tracked_symbols:
                if symbol in gecko_data:
                    kucoin_symbol = symbol.upper().replace("-", "")
                    if kucoin_symbol == "MATICNETWORK":
                        kucoin_symbol = "MATIC"
                    kc_data = self.kucoin.get_price(f"{kucoin_symbol}-USDT")
                    if "error" not in kc_data:
                        gecko_price_data = {
                            "symbol": symbol.upper(),
                            "price": gecko_data[symbol]["usd"],
                            "source": "CoinGecko"
                        }
                        comparison = self.redundancy.check_price_discrepancy(
                            gecko_price_data, kc_data, tolerance=0.02
                        )
                        self.db.log_price_check(
                            symbol=symbol.upper(),
                            price1=comparison.get("price1", 0),
                            price2=comparison.get("price2", 0),
                            diff_percent=comparison.get("diff_percent", 0),
                            status=comparison.get("status", "error")
                        )
                        if comparison["status"] == "OK":
                            consolidated_data[symbol.upper()] = {
                                "price": comparison["avg_price"],
                                "change_24h": gecko_data[symbol]["usd_24h_change"],
                                "timestamp": time.time(),
                                "source": "consolidated"
                            }
        return consolidated_data
    
    def detect_and_analyze_anomalies(self, market_data: Dict):
        market_condition = self.detector.detect_market_condition(market_data)
        self.db.log_market_condition(
            len(market_condition['green_coins']),
            len(market_condition['red_coins']),
            market_condition['total_coins'],
            market_condition['is_anomaly']
        )
        if not market_condition['is_anomaly']:
            self.logger.info("No market anomaly detected")
            return None
        self.logger.info(f"Market anomaly detected! Green coins: {len(market_condition['green_coins'])}, Red coins: {len(market_condition['red_coins'])}")
        best_anomaly = None
        highest_confidence = 0
        for green_coin in market_condition['green_coins']:
            symbol = green_coin['symbol']
            news_data = self.cryptopanic.get_news(symbol, filter="rising")
            coin_anomaly_data = {
                'is_anomaly': True,
                'green_coins': [green_coin],
                'red_coins': market_condition['red_coins'],
                'total_coins': market_condition['total_coins']
            }
            analysis = self.detector.analyze_anomaly_strength(coin_anomaly_data, news_data)
            if analysis['confidence'] > highest_confidence:
                highest_confidence = analysis['confidence']
                best_anomaly = {
                    'symbol': symbol,
                    'price': green_coin['price'],
                    'change_24h': green_coin['change'],
                    'confidence': analysis['confidence'],
                    'reasons': analysis['reasons'],
                    'news': news_data
                }
        return best_anomaly
    
    def execute_trade_strategy(self, anomaly_data: Dict):
        if anomaly_data['confidence'] < self.min_confidence:
            self.logger.info(f"Confidence too low for {anomaly_data['symbol']}: {anomaly_data['confidence']}%")
            return False
        symbol = anomaly_data['symbol']
        entry_price = anomaly_data['price']
        stop_loss = self.risk_manager.calculate_stop_loss(entry_price, volatility=0.08)
        take_profit = self.risk_manager.calculate_take_profit(entry_price, risk_reward_ratio=3.0, stop_loss=stop_loss)
        portfolio_value = self.kucoin.get_account_balance("USDT")
        if isinstance(portfolio_value, dict) and "error" in portfolio_value:
            self.logger.error(f"Error getting portfolio value: {portfolio_value['error']}")
            return False
        position_size_info = self.risk_manager.calculate_position_size(
            entry_price, stop_loss, portfolio_value
        )
        if "error" in position_size_info:
            self.logger.error(f"Error calculating position size: {position_size_info['error']}")
            return False
        self.db.log_anomaly_signal(
            symbol, entry_price, anomaly_data['change_24h'],
            anomaly_data['confidence'], anomaly_data['reasons']
        )
        self.db.log_trade(
            symbol, entry_price, stop_loss, take_profit,
            position_size_info['position_size'], position_size_info['risk_amount'],
            anomaly_data['confidence']
        )
        # Siapkan data untuk Telegram output (multi-thread edukatif)
        market_context = {
            "anomaly_summary": f"{', '.join(anomaly_data['reasons'][:2])}",
            "data_summary": (
                f"24h Change: {anomaly_data['change_24h']}%, "
                f"News: {anomaly_data['news'].get('news_count',0)} berita"
            ),
            "catalyst": anomaly_data['news']['news'][0]['title'] if anomaly_data['news']['news'] else "Tidak ada catalyst"
        }
        position_info = {
            "entry_price": entry_price,
            "stop_loss_price": stop_loss,
            "risk_percentage": position_size_info['risk_percentage'],
            "risk_amount": position_size_info['risk_amount'],
        }
        self.telegram.send_anomaly_layak_battle(anomaly_data, position_info, market_context)
        self.logger.info(f"🚨 TRADE SIGNAL FOR {symbol}")
        self.logger.info(f"   Entry: ${entry_price:.4f}")
        self.logger.info(f"   Stop Loss: ${stop_loss:.4f} (-{((entry_price-stop_loss)/entry_price*100):.2f}%)")
        self.logger.info(f"   Take Profit: ${take_profit:.4f} (+{((take_profit-entry_price)/entry_price*100):.2f}%)")
        self.logger.info(f"   Position Size: {position_size_info['position_size']:.4f} {symbol}")
        self.logger.info(f"   Risk Amount: ${position_size_info['risk_amount']:.2f}")
        self.logger.info(f"   Confidence: {anomaly_data['confidence']}%")
        self.logger.info(f"   Reasons: {', '.join(anomaly_data['reasons'][:2])}")
        return True
    
    def run_single_iteration(self):
        self.logger.info("Starting market data check...")
        try:
            market_data = self.fetch_market_data()
            if not market_data:
                self.logger.warning("No market data retrieved")
                return
            best_anomaly = self.detect_and_analyze_anomalies(market_data)
            if best_anomaly:
                self.execute_trade_strategy(best_anomaly)
            else:
                self.logger.info("No strong anomaly found for trading")
        except Exception as e:
            self.logger.error(f"Error during iteration: {e}")
        self.logger.info("Market data check completed\n")

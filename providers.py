import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

class CoinGeckoProvider:
    """Provider data harga dari CoinGecko API (gratis)"""
    
    BASE_URL = "https://api.coingecko.com/api/v3/simple/price"
    
    @staticmethod
    def get_price(symbol="bitcoin", vs_currency="usd"):
        """
        Ambil harga terkini dari CoinGecko API
        Mengembalikan: dict {symbol, price, timestamp, source} atau {error}
        """
        try:
            url = f"{CoinGeckoProvider.BASE_URL}?ids={symbol}&vs_currencies={vs_currency}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "symbol": symbol.upper(),
                "price": float(data[symbol][vs_currency]),
                "timestamp": time.time(),
                "source": "CoinGecko"
            }
        except Exception as e:
            return {"error": str(e), "source": "CoinGecko"}


class KucoinProvider:
    """Provider data harga dari KuCoin API (terautentikasi)"""
    
    def __init__(self):
        self.base_url = "https://api.kucoin.com"
        self.api_key = os.getenv("KUCOIN_API_KEY")
        self.api_secret = os.getenv("KUCOIN_API_SECRET")
        self.api_passphrase = os.getenv("KUCOIN_API_PASSPHRASE")
    
    def get_price(self, symbol="BTC-USDT"):
        """
        Ambil harga terkini dari KuCoin API
        Mengembalikan: dict {symbol, price, timestamp, source} atau {error}
        """
        try:
            # Endpoint public tidak membutuhkan autentikasi
            url = f"{self.base_url}/api/v1/market/orderbook/level1?symbol={symbol}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] == '200000':
                return {
                    "symbol": symbol,
                    "price": float(data['data']['price']),
                    "timestamp": time.time(),
                    "source": "KuCoin"
                }
            else:
                return {"error": data['msg'], "source": "KuCoin"}
                
        except Exception as e:
            return {"error": str(e), "source": "KuCoin"}

import logging
from ratelimit import limits, sleep_and_retry, RateLimitException
import os
import time
import requests
import hmac
import hashlib
import base64
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO
)

# Rate limit constants
COINGECKO_RATE_LIMIT = 50  # max 50 calls per minute (CoinGecko doc: 10-50/min)
KUCOIN_RATE_LIMIT = 10     # max 10 calls per second (Kucoin doc)
CRYPTOPANIC_RATE_LIMIT = 5 # max 5 calls per second (CryptoPanic free)

def log_rate_limit(calls, period):
    def decorator(func):
        @sleep_and_retry
        @limits(calls=calls, period=period)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RateLimitException as e:
                msg = f"Rate limit hit for {func.__name__}, sleeping for {period} seconds."
                logging.warning(msg)
                # Optional: Integrasi alert Telegram di sini
                raise e
        return wrapper
    return decorator

class CoinGeckoProvider:
    BASE_URL = "https://api.coingecko.com/api/v3"

    @staticmethod
    @log_rate_limit(COINGECKO_RATE_LIMIT, 60)
    def get_price(symbol="bitcoin", vs_currency="usd"):
        try:
            url = f"{CoinGeckoProvider.BASE_URL}/simple/price?ids={symbol}&vs_currencies={vs_currency}&include_24hr_change=true"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                "symbol": symbol.upper(),
                "price": float(data[symbol][vs_currency]),
                "change_24h": float(data[symbol][f"{vs_currency}_24h_change"]),
                "timestamp": time.time(),
                "source": "CoinGecko"
            }
        except Exception as e:
            return {"error": str(e), "source": "CoinGecko"}

    @staticmethod
    @log_rate_limit(COINGECKO_RATE_LIMIT, 60)
    def get_market_data(symbols=["bitcoin", "ethereum"], vs_currency="usd"):
        try:
            symbols_str = ",".join(symbols)
            url = f"{CoinGeckoProvider.BASE_URL}/simple/price?ids={symbols_str}&vs_currencies={vs_currency}&include_24hr_change=true"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

class KucoinProvider:
    def __init__(self):
        self.base_url = "https://api.kucoin.com"
        self.api_key = os.getenv("KUCOIN_API_KEY")
        self.api_secret = os.getenv("KUCOIN_API_SECRET")
        self.api_passphrase = os.getenv("KUCOIN_API_PASSPHRASE")
    
    def _create_signature(self, method, endpoint, body=""):
        now = str(int(time.time() * 1000))
        str_to_sign = now + method + endpoint + body
        signature = base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                str_to_sign.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        passphrase_sign = base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                self.api_passphrase.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        return {
            "KC-API-KEY": self.api_key,
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": now,
            "KC-API-PASSPHRASE": passphrase_sign,
            "KC-API-KEY-VERSION": "2"
        }
    
    @log_rate_limit(KUCOIN_RATE_LIMIT, 1)
    def get_price(self, symbol="BTC-USDT"):
        try:
            url = f"{self.base_url}/api/v1/market/orderbook/level1?symbol={symbol}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data['code'] == '200000':
                return {
                    "symbol": symbol.split('-')[0],
                    "price": float(data['data']['price']),
                    "timestamp": time.time(),
                    "source": "KuCoin"
                }
            else:
                return {"error": data['msg'], "source": "KuCoin"}
        except Exception as e:
            return {"error": str(e), "source": "KuCoin"}
    
    @log_rate_limit(KUCOIN_RATE_LIMIT, 1)
    def get_account_balance(self, currency="USDT"):
        try:
            endpoint = "/api/v1/accounts"
            headers = self._create_signature("GET", endpoint)
            headers["Content-Type"] = "application/json"
            response = requests.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data['code'] == '200000':
                for account in data['data']:
                    if account['currency'] == currency and account['type'] == 'trade':
                        return float(account['balance'])
                return 0.0
            else:
                return {"error": data['msg']} 
        except Exception as e:
            return {"error": str(e)}

class CryptoPanicProvider:
    BASE_URL = "https://cryptopanic.com/api/v1"
    def __init__(self):
        self.api_key = os.getenv("CRYPTOPANIC_API_KEY", "")
    @log_rate_limit(CRYPTOPANIC_RATE_LIMIT, 1)
    def get_news(self, symbol="BTC", filter="rising"):
        try:
            url = f"{self.BASE_URL}/posts/?auth_token={self.api_key}&currencies={symbol}&filter={filter}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                "symbol": symbol,
                "news_count": len(data['results']),
                "news": data['results'][:3],
                "timestamp": time.time(),
                "source": "CryptoPanic"
            }
        except Exception as e:
            return {"error": str(e), "source": "CryptoPanic"}
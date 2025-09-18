import os
import time
import requests
import hmac
import hashlib
import base64
from dotenv import load_dotenv

load_dotenv()

class CoinGeckoProvider:
    BASE_URL = "https://api.coingecko.com/api/v3"
    @staticmethod
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

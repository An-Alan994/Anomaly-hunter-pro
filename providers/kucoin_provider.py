import time, hmac, base64, hashlib, requests
from functools import wraps
from utils.config import Config

def rate_limited(max_per_minute):
    """Decorator rate limit"""
    min_interval = 60.0 / max_per_minute
    def decorator(func):
        last_called = [0.0]
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            last_called[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

class KucoinProvider:
    BASE_URL = "https://api.kucoin.com"

    def __init__(self):
        self.api_key = Config.KUCOIN_KEY
        self.api_secret = Config.KUCOIN_SECRET
        self.passphrase = Config.KUCOIN_PASSPHRASE

    def generate_signature(self, str_to_sign):
        return base64.b64encode(
            hmac.new(self.api_secret.encode(), str_to_sign.encode(), hashlib.sha256).digest()
        ).decode()

    @rate_limited(30)
    def get_price(self, symbol="BTC-USDT"):
        resp = requests.get(f"{self.BASE_URL}/api/v1/market/orderbook/level1?symbol={symbol}")
        return float(resp.json()["data"]["price"])

    def place_order(self, symbol, side, size, price=None, order_type="limit"):
        """Eksekusi order nyata"""
        endpoint = "/api/v1/orders"
        url = self.BASE_URL + endpoint
        payload = {
            "clientOid": str(int(time.time() * 1000)),
            "side": side,
            "symbol": symbol,
            "type": order_type,
            "size": str(size)
        }
        if order_type == "limit" and price:
            payload["price"] = str(price)
        headers = {"KC-API-KEY": self.api_key}
        return requests.post(url, json=payload, headers=headers).json()

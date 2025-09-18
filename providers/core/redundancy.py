class RedundancyManager:
    """Cross-check harga antar provider"""
    def check_price_discrepancy(self, prices: dict, tolerance: float = 0.5):
        """
        prices: {"kucoin": 27100, "coingecko": 27105}
        tolerance: max selisih %
        """
        values = list(prices.values())
        avg = sum(values) / len(values)
        for provider, val in prices.items():
            if abs(val - avg) / avg * 100 > tolerance:
                return False, provider
        return True, None

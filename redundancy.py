class RedundancyManager:
    def check_price_discrepancy(self, data1, data2, tolerance=0.02):
        price1 = float(data1.get("price", 0))
        price2 = float(data2.get("price", 0))
        if price1 == 0 or price2 == 0:
            return {"status": "error", "price1": price1, "price2": price2, "diff_percent": 0, "avg_price": 0}
        diff_percent = abs(price1 - price2) / ((price1 + price2) / 2)
        avg_price = (price1 + price2) / 2
        status = "OK" if diff_percent <= tolerance else "MISMATCH"
        return {
            "status": status,
            "price1": price1,
            "price2": price2,
            "diff_percent": diff_percent * 100,
            "avg_price": avg_price
        }

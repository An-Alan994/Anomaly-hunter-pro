class RedundancyManager:
    """Manajer pemeriksaan konsistensi data antar multiple provider"""
    
    @staticmethod
    def check_price_discrepancy(price_data_1, price_data_2, tolerance=0.01):
        """
        Bandingkan harga dari dua provider berbeda
        tolerance: persentase perbedaan maksimal yang diizinkan (default 1%)
        Mengembalikan: dict dengan hasil perbandingan
        """
        if "error" in price_data_1 or "error" in price_data_2:
            return {
                "status": "error",
                "provider1": price_data_1,
                "provider2": price_data_2
            }
        
        price1 = price_data_1["price"]
        price2 = price_data_2["price"]
        avg_price = (price1 + price2) / 2
        diff_percent = abs(price1 - price2) / avg_price
        
        return {
            "price1": price1,
            "price2": price2,
            "avg_price": avg_price,
            "diff_percent": round(diff_percent * 100, 4),
            "status": "OK" if diff_percent <= tolerance else "DISCREPANCY",
            "timestamp": time.time()
        }

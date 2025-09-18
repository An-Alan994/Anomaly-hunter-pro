import time
import logging
from typing import Dict, List, Optional

class AnomalyDetector:
    """Detektor anomali harga untuk strategi 'Long Only The Anomaly'"""
    
    def __init__(self, threshold_green: float = 0.5, threshold_red: float = -1.0):
        self.threshold_green = threshold_green  # Minimal perubahan positif untuk dianggap hijau
        self.threshold_red = threshold_red      # Maksimal perubahan negatif untuk dianggap merah
        self.logger = logging.getLogger(__name__)
    
    def detect_market_condition(self, market_data: Dict) -> Dict:
        """
        Deteksi kondisi market: apakah ada anomaly (hijau di lautan merah)
        Mengembalikan: dict dengan hasil deteksi
        """
        green_coins = []
        red_coins = []
        
        for symbol, data in market_data.items():
            if 'change_24h' in data:
                change = data['change_24h']
                if change > self.threshold_green:
                    green_coins.append({
                        'symbol': symbol,
                        'change': change,
                        'price': data.get('price', 0)
                    })
                elif change < self.threshold_red:
                    red_coins.append({
                        'symbol': symbol,
                        'change': change,
                        'price': data.get('price', 0)
                    })
        
        # Deteksi anomaly: hanya 1-2 coin hijau, minimal 3 coin merah
        is_anomaly = len(green_coins) <= 2 and len(red_coins) >= 3 and len(green_coins) > 0
        
        return {
            'is_anomaly': is_anomaly,
            'green_coins': green_coins,
            'red_coins': red_coins,
            'total_coins': len(market_data),
            'timestamp': time.time()
        }
    
    def analyze_anomaly_strength(self, anomaly_data: Dict, news_data: Optional[Dict] = None) -> Dict:
        """
        Analisis kekuatan anomaly berdasarkan berbagai faktor
        Mengembalikan: confidence score (0-100)
        """
        if not anomaly_data['is_anomaly']:
            return {'confidence': 0, 'reasons': ['No anomaly detected']}
        
        confidence = 0
        reasons = []
        
        # Factor 1: Strength of green performance
        green_strength = sum(coin['change'] for coin in anomaly_data['green_coins']) / len(anomaly_data['green_coins'])
        if green_strength > 2.0:
            confidence += 25
            reasons.append(f"Strong green performance (+{green_strength:.2f}%)")
        elif green_strength > 1.0:
            confidence += 15
            reasons.append(f"Moderate green performance (+{green_strength:.2f}%)")
        else:
            confidence += 5
            reasons.append(f"Weak green performance (+{green_strength:.2f}%)")
        
        # Factor 2: Market red intensity
        red_intensity = abs(sum(coin['change'] for coin in anomaly_data['red_coins']) / len(anomaly_data['red_coins']))
        if red_intensity > 2.0:
            confidence += 20
            reasons.append(f"Strong red market intensity (-{red_intensity:.2f}%)")
        elif red_intensity > 1.0:
            confidence += 15
            reasons.append(f"Moderate red market intensity (-{red_intensity:.2f}%)")
        
        # Factor 3: News sentiment (if available)
        if news_data and 'news_count' in news_data and news_data['news_count'] > 0:
            confidence += 15
            reasons.append(f"Positive news coverage ({news_data['news_count']} articles)")
        
        # Factor 4: Ratio of green to red coins
        green_ratio = len(anomaly_data['green_coins']) / anomaly_data['total_coins']
        if green_ratio < 0.2:  # Less than 20% are green
            confidence += 20
            reasons.append("Strong anomaly ratio (few green among many red)")
        elif green_ratio < 0.3:
            confidence += 10
            reasons.append("Moderate anomaly ratio")
        
        # Cap at 100
        confidence = min(confidence, 100)
        
        return {
            'confidence': confidence,
            'reasons': reasons,
            'anomaly_coins': [coin['symbol'] for coin in anomaly_data['green_coins']],
            'timestamp': time.time()
      }

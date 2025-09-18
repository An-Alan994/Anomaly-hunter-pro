class RiskManager:
    """Manajer risiko untuk perhitungan position sizing dan stop-loss"""
    
    def __init__(self, max_risk_per_trade: float = 0.02, max_portfolio_risk: float = 0.1):
        self.max_risk_per_trade = max_risk_per_trade  # 2% risk per trade
        self.max_portfolio_risk = max_portfolio_risk  # 10% max risk portfolio
    
    def calculate_position_size(self, entry_price: float, stop_loss: float, 
                              portfolio_value: float) -> Dict:
        """
        Hitung ukuran posisi berdasarkan risiko
        Mengembalikan: size yang direkomendasikan
        """
        risk_per_coin = entry_price - stop_loss
        if risk_per_coin <= 0:
            return {"error": "Stop loss must be below entry price"}
        
        max_risk_amount = portfolio_value * self.max_risk_per_trade
        position_size = max_risk_amount / risk_per_coin
        
        return {
            'position_size': position_size,
            'risk_amount': max_risk_amount,
            'risk_percentage': self.max_risk_per_trade * 100,
            'stop_loss_price': stop_loss,
            'entry_price': entry_price
        }
    
    def calculate_stop_loss(self, entry_price: float, volatility: float = 0.05) -> float:
        """
        Hitung stop loss berdasarkan volatilitas
        volatility: persentase pergerakan normal (default 5%)
        """
        return entry_price * (1 - volatility)
    
    def calculate_take_profit(self, entry_price: float, risk_reward_ratio: float = 3.0, 
                             stop_loss: float = None) -> float:
        """
        Hitung take profit berdasarkan risk-reward ratio
        """
        if stop_loss is None:
            stop_loss = self.calculate_stop_loss(entry_price)
        
        risk_amount = entry_price - stop_loss
        return entry_price + (risk_amount * risk_reward_ratio)

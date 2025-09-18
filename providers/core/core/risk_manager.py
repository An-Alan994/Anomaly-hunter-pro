from utils.config import Config

class RiskManager:
    def __init__(self, balance=1000):
        self.balance = balance

    def calculate_position_size(self, stop_loss_pct=0.01):
        risk_amount = self.balance * Config.RISK_PER_TRADE
        return round(risk_amount / stop_loss_pct, 4)

    def check_portfolio_exposure(self, open_positions, max_open=3):
        return len(open_positions) < max_open

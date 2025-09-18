import os
import requests

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    def send_message(self, text, reply_to_message_id=None):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }
        if reply_to_message_id is not None:
            payload["reply_to_message_id"] = reply_to_message_id
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        if "result" in result:
            return result["result"]["message_id"]
        return None

    def send_anomaly_layak_battle(self, anomaly_data, position_info, market_context):
        # 1. Pesan Utama (ALERT CEPAT)
        alert_msg = (
            f"🚨 *{anomaly_data['symbol']}* | Skor: *{anomaly_data['confidence']}/100*\n"
            f"*LONG* | Entry: `${position_info['entry_price']:.2f}` | SL: `${position_info['stop_loss_price']:.2f}` | R/R: 1:3"
        )
        main_id = self.send_message(alert_msg)
        
        # 2. Thread 1 (Inti Anomali)
        anomaly_msg = f"⛏️ *Anomali*: {market_context['anomaly_summary']}"
        self.send_message(anomaly_msg, reply_to_message_id=main_id)
        
        # 3. Thread 2 (Data Inti)
        data_msg = f"🔍 *Konfirmasi*: {market_context['data_summary']}"
        self.send_message(data_msg, reply_to_message_id=main_id)
        
        # 4. Thread 3 (Catalyst Fundamental)
        if market_context.get('catalyst'):
            catalyst_msg = f"💡 *Catalyst*: {market_context['catalyst']}"
            self.send_message(catalyst_msg, reply_to_message_id=main_id)
        
        # 5. Thread 4 (Risk Management)
        risk_msg = (
            f"⚔️ *Risk*: Maks {position_info['risk_percentage']:.1f}% equity, "
            f"max loss `${position_info['risk_amount']:.2f}` jika SL."
        )
        self.send_message(risk_msg, reply_to_message_id=main_id)
        return main_id

import logging, json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name="anomaly-hunter"):
        self.logger = logging.getLogger(name)
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    def log_trade_signal(self, signal_data):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "trade_signal",
            "data": signal_data
        }
        self.logger.info(json.dumps(log_entry))

# from celery.exceptions import TimeoutError, TimeLimitExceeded

from datetime import datetime
from src.loguru_config import logger
from src.kafka_producer import save_add_alarm_about_new_pool_by_kafka


class TokenPriceCollector:
    def __init__(self):
        self.intervals = [1, 2, 5, 10, 15, 30, 45, 60, 90, 180, 360, 720, 1440]

    async def listen_new_tokens(self):
        raise NotImplementedError

    def save_token(self, address: str, dex_name: str, network: str, created_at: datetime) -> bool:
        logger.info(f'NewToken {address = }, {dex_name = }, {network = }, {created_at = } \n')
        try:
            save_add_alarm_about_new_pool_by_kafka(address, dex_name, network, created_at)
            return True
        except Exception as err:
            logger.error(f"TimeoutError: {err}")
            return False

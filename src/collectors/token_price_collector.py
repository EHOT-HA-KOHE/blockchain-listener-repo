# from celery.exceptions import TimeoutError, TimeLimitExceeded

from src.loguru_config import logger
# from src.celery_tasks import wait_token_on_dexscreener, track_price     # todo


class TokenPriceCollector:
    def __init__(self):
        self.intervals = [1, 2, 5, 10, 15, 30, 45, 60, 90, 180, 360, 720, 1440]

    async def listen_new_tokens(self):
        raise NotImplementedError

    def save_token(self, address: str, dex_name: str, network: str) -> bool:
        token_info = {
            'address': address, 
            'dex_name': dex_name, 
            'network': network,
        }
        print(f'{token_info} \n')
        try:
            # res = wait_token_on_dexscreener.delay(address, dex_name, network)
            # is_success = res.get()
            is_success = True
        # except TimeLimitExceeded as err:
        #     logger.error(f"TimeLimitExceeded: {err}")
        #     is_success = False
        except TimeoutError as err:
            logger.error(f"TimeoutError: {err}")
            is_success = False

        if is_success:
            logger.info(f'write to db token_price in 0 delay')
            for interval in self.intervals:
                interval *= 60
                # track_price.apply_async((address, interval, dex_name, network,), countdown=interval)
            return True
        return False

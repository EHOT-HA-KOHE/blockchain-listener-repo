import time
import requests

from celery.utils.log import get_task_logger
from celery.exceptions import Retry, MaxRetriesExceededError, SoftTimeLimitExceeded

from src.celery import app
from src.consts import SOL_MINT
from src.database import PgUtils
from src.env import DexScreenerEnv
from src.utils import get_portal_url_from_pair_info

logger = get_task_logger(__name__)


@app.task(bind=True, max_retries=3, time_limit=86520, soft_time_limit=86400, default_retry_delay=30)
def wait_token_on_dexscreener(self, address: str, dex_name: str, network: str, inter_iter_delay: int = 30) -> bool:
    """
    Explains the time limits parameters in Celery task configuration.

    Parameters:
    - time_limit: Sets a strict time limit for task execution. If the task exceeds this limit,
      it is forcefully terminated by Celery without the ability to catch the TimeLimitExceeded exception.
    - soft_time_limit: Sets a soft time limit for task execution. When the task approaches this limit,
      a SoftTimeLimitExceeded exception is raised, allowing the task to handle the interruption and clean up.
      If not caught, the task continues until it reaches the hard time limit (time_limit), if set.

    Note:
    - The TimeLimitExceeded error is handled at the point of waiting for the task result.
    - The SoftTimeLimitExceeded error is handled at the task.
    """
    dexscreener_url = DexScreenerEnv().connect_str

    with PgUtils() as db:
        while True:
            try:
                url = f'{dexscreener_url}/get_token_info/?token_address={address}'
                response = requests.get(url)

                if response.status_code != 200:
                    logger.error(f"Response status code is not 200. Code: {response.status_code}")
                    self.retry()

                response_json_data = response.json()[address]
                if response_json_data['status_code'] != 200:
                    logger.error(
                        f"Response status code in response is not 200. Code: {response_json_data['status_code']}")
                    self.retry()

                if pairs_info := response_json_data['response_data']['pairs']:
                    for pair in pairs_info:
                        if pair['dexId'] == "raydium" and pair['quoteToken']['address'] == SOL_MINT:
                            logger.info(f'write to db token_price in 0 delay')

                            token_from_db = db.get_token_by_address(address)
                            portal_url = get_portal_url_from_pair_info(pair)

                            if not token_from_db:
                                db.store_token(
                                    pair['baseToken']['name'],
                                    pair['baseToken']['symbol'],
                                    pair['baseToken']['address'],
                                    "Unknown",
                                    network,
                                    portal_url,
                                )
                            elif not token_from_db['portal_url'] and portal_url:
                                db.update_token_portal_url(
                                    token_from_db['address'],
                                    get_portal_url_from_pair_info(pair),
                                )

                            db.store_token_price(
                                token_from_db['id'],
                                pair['priceNative'],
                                pair['liquidity']['quote'],
                                0,
                                dex_name
                            )
                            return True

                time.sleep(inter_iter_delay)

            except Retry as err:
                raise err

            except MaxRetriesExceededError as err:
                logger.error(f'MaxRetriesExceededError {getattr(self, "max_retries") = } - {err}')
                return False

            except SoftTimeLimitExceeded as err:
                logger.error(f'SoftTimeLimitExceeded {getattr(self, "soft_time_limit") = } - {err}')
                return False

            except Exception as err:
                logger.error(err)
                try:
                    self.retry()
                except MaxRetriesExceededError as err:
                    logger.error(f'MaxRetriesExceededError {getattr(self, "max_retries") = } - {err}')
                    return False


@app.task
def track_price(address: str, delay: int, dex_name: str, network: str) -> str | None:
    dexscreener_url = DexScreenerEnv().connect_str

    try:
        url = f'{dexscreener_url}/get_token_info/?token_address={address}'
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"Response status code is not 200. Code: {response.status_code}")

        response_json_data = response.json()[address]
        if response_json_data['status_code'] != 200:
            raise Exception(f"Response status code in response is not 200. Code: {response_json_data['status_code']}")

        if pairs_info := response_json_data['response_data']['pairs']:
            for pair in pairs_info:
                if pair['dexId'] == "raydium" and pair['quoteToken']['address'] == SOL_MINT:
                    logger.info(f'write to db token_price in {delay} delay')

                    with PgUtils() as db:
                        token_from_db = db.get_token_by_address(address)

                        if not token_from_db['portal_url']:
                            portal_url = get_portal_url_from_pair_info(pair)
                            if portal_url:
                                db.update_token_portal_url(
                                    token_from_db['address'],
                                    get_portal_url_from_pair_info(pair),
                                )

                        db.store_token_price(
                            token_from_db['id'],
                            pair['priceNative'],
                            pair['liquidity']['quote'],
                            delay,
                            dex_name
                        )

                    return f"End of tracking prices for {address} in {delay} sec delay after start"
        else:
            logger.error("The address whose information has already been obtained from Dexscreener "
                         "does not now exist on Dexscreener now")

    except Exception as err:
        logger.info(f'write to db token_price in {delay} delay')
        logger.error(err)

import asyncio
import threading
import warnings
import os
import time

from dotenv import load_dotenv

from web3.exceptions import MismatchedABI   # dont del need for filterwarnings

from src.loguru_config import logger
from src.collectors import (RadiumPriceCollector,
                            EthUniswapV2PriceCollector, EthUniswapV3PriceCollector,
                            BaseUniswapV2PriceCollector)


warnings.filterwarnings("ignore", category=UserWarning, message=".*MismatchedABI.*")
load_dotenv('.env')


def run_async_function(async_func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(async_func())
    loop.run_forever()


if __name__ == '__main__':
    radium_collector = RadiumPriceCollector()

    eth_uniswap_v2_collector = EthUniswapV2PriceCollector(
        wss_rpc=os.getenv('ETH_WSS_RPC'))
    eth_uniswap_v3_collector = EthUniswapV3PriceCollector(
        wss_rpc=os.getenv('ETH_WSS_RPC'))
    base_uniswap_v2_collector = BaseUniswapV2PriceCollector(
        wss_rpc=os.getenv('BASE_WSS_RPC'))

    # ================================

    # eth_uniswap_v2_collector = EthUniswapV2PriceCollector(
    #     wss_rpc=os.getenv('ETH_WSS_RPC'))
    # asyncio.run(eth_uniswap_v2_collector.listen_new_tokens())

    # eth_uniswap_v3_collector = EthUniswapV3PriceCollector(
    #     wss_rpc=os.getenv('ETH_WSS_RPC'))
    # asyncio.run(eth_uniswap_v3_collector.listen_new_tokens())

    # ================================

    # base_uniswap_v2_collector = BaseUniswapV2PriceCollector(
    #     wss_rpc=os.getenv('BASE_WSS_RPC'))
    # asyncio.run(base_uniswap_v2_collector.listen_new_tokens())

    # ================================

    thread_1 = threading.Thread(target=run_async_function, args=(radium_collector.listen_new_tokens,))
    # thread_2 = threading.Thread(target=run_async_function, args=(eth_uniswap_v2_collector.listen_new_tokens,))
    # thread_3 = threading.Thread(target=run_async_function, args=(eth_uniswap_v3_collector.listen_new_tokens,))
    thread_4 = threading.Thread(target=run_async_function, args=(base_uniswap_v2_collector.listen_new_tokens,))

    thread_1.start()
    # thread_2.start()
    # thread_3.start()
    thread_4.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")

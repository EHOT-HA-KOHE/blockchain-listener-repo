import json
import asyncio

from web3 import Web3
from web3.datastructures import AttributeDict

from src.loguru_config import logger
from src.collectors.token_price_collector import TokenPriceCollector


class UniswapPriceCollector(TokenPriceCollector):
    dex_name = 'UNISWAP'
    pair_created_event_signature = None
    event_filter = None

    def __init__(
            self,
            wss_rpc: str,
            uniswap_factory_address_str: str,
            network: str,
            native_token_address: str,
            abi_file_path: str
    ):
        super().__init__()
        self.network = network
        self.native_token_address = native_token_address

        self.uniswap_factory_address = Web3.to_checksum_address(uniswap_factory_address_str)
        self.wss_rpc = wss_rpc
        self.web3 = Web3(Web3.WebsocketProvider(wss_rpc))

        self.uniswap_factory_abi = self.set_abi(abi_file_path)
        self.uniswap_factory = self.set_factory()

    @staticmethod
    def set_abi(abi_file_path):
        with open(abi_file_path, 'r') as abi:
            return json.load(abi)

    def set_factory(self):
        return self.web3.eth.contract(address=self.uniswap_factory_address, abi=self.uniswap_factory_abi)

    def set_event_signature(self):
        raise NotImplementedError

    def set_event_filter(self):
        if self.pair_created_event_signature is None:
            raise ValueError
        event_filter = self.web3.eth.filter({
            'address': self.uniswap_factory_address,
            'topics': [self.pair_created_event_signature]
        })
        return event_filter

    def get_address_from_event(self, event: AttributeDict) -> str | None:
        raise NotImplementedError

    async def process_new_token(self, event: AttributeDict):
        address = self.get_address_from_event(event)
        self.save_token(address, self.dex_name, self.network)

    async def listen_new_tokens(self, poll_interval=2):
        if self.event_filter is None:
            raise ValueError
        while True:
            try:
                for event in self.event_filter.get_new_entries():
                    task = asyncio.create_task(self.process_new_token(event))

                await asyncio.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Error: {e}")

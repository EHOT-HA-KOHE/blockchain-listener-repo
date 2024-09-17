import json
import asyncio

from web3 import Web3
from web3.datastructures import AttributeDict

from src.loguru_config import logger
from src.collectors.token_price_collector import TokenPriceCollector


class UniswapBasePriceCollector(TokenPriceCollector):
    dex_name = 'UNISWAP'
    network = 'BASE'
    base_token_address = '0xBaseTokenAddressHere'  # Замените на фактический адрес токена Base

    def __init__(
            self,
            wss_rpc: str,
            uniswap_v2_factory_address_str: str = '0xBaseUniswapFactoryAddressHere',  # Замените на фактический адрес фабрики Uniswap в сети Base
    ):
        super().__init__()
        self.uniswap_v2_factory_address = Web3.to_checksum_address(uniswap_v2_factory_address_str)
        self.wss_rpc = wss_rpc
        self.web3 = Web3(Web3.WebsocketProvider(wss_rpc))
        self.uniswap_v2_factory_abi = self.set_abi()
        self.uniswap_v2_factory = self.set_factory()
        self.pair_created_event_signature = self.set_event_signature()
        self.event_filter = self.set_event_filter()

    @staticmethod
    def set_abi():
        with open('base_uniswap_abi.json', 'r') as abi:
            return json.load(abi)

    def set_factory(self):
        return self.web3.eth.contract(address=self.uniswap_v2_factory_address, abi=self.uniswap_v2_factory_abi)

    def set_event_signature(self):
        pair_created_event_abi = (next(item for item in self.uniswap_v2_factory_abi
                                       if item['type'] == 'event' and item['name'] == 'PairCreated'))
        sig = self.web3.keccak(
            text=f"{pair_created_event_abi['name']}"
                 f"({','.join([param['type'] for param in pair_created_event_abi['inputs']])})"
        ).hex()
        return sig

    def set_event_filter(self):
        event_filter = self.web3.eth.filter({
            'address': self.uniswap_v2_factory_address,
            'topics': [self.pair_created_event_signature]
        })
        return event_filter

    def get_address_from_event(self, event: AttributeDict) -> str | None:
        transaction_hash = event['transactionHash']
        receipt = self.web3.eth.wait_for_transaction_receipt(transaction_hash)
        logs = self.uniswap_v2_factory.events.PairCreated().process_receipt(receipt)

        for log in logs:
            token0 = log['args']['token0']
            token1 = log['args']['token1']
            pair = log['args']['pair']

            new_token = token0 if token0 != self.base_token_address else token1
            return new_token

        return None

    async def process_new_token(self, event: AttributeDict):
        address = self.get_address_from_event(event)
        self.save_token(address, self.dex_name, self.network)

    async def listen_new_tokens(self, poll_interval=2):
        while True:
            try:
                for event in self.event_filter.get_new_entries():
                    task = asyncio.create_task(self.process_new_token(event))

                await asyncio.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Error: {e}")

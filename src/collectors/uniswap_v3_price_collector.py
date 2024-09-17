from web3.datastructures import AttributeDict

from src.collectors.uniswap_price_collector import UniswapPriceCollector


class UniswapV3PriceCollector(UniswapPriceCollector):
    
    dex_name = 'UNISWAP_V2'

    def __init__(
            self,
            wss_rpc: str,
            uniswap_v3_factory_address_str: str,
            network,
            native_token_address,
            abi_file_path
    ):
        super().__init__(
            wss_rpc,
            uniswap_v3_factory_address_str,
            network,
            native_token_address,
            abi_file_path
        )

        self.pair_created_event_signature = self.set_event_signature()
        self.event_filter = self.set_event_filter()

    def set_event_signature(self):
        pair_created_event_abi = next(item for item in self.uniswap_factory_abi if
                                      item['type'] == 'event' and item['name'] == 'PoolCreated')
        sig = self.web3.keccak(
            text=f"{pair_created_event_abi['name']}({','.join(param['type'] for param in pair_created_event_abi['inputs'])})"
        ).hex()
        return sig

    def get_address_from_event(self, event: AttributeDict) -> str | None:
        transaction_hash = event['transactionHash']
        receipt = self.web3.eth.wait_for_transaction_receipt(transaction_hash)
        logs = self.uniswap_factory.events.PoolCreated().process_receipt(receipt)

        for log in logs:
            token0 = log['args']['token0']
            token1 = log['args']['token1']
            pair = log['args']['pool']

            new_token = token0 if token0 != self.native_token_address else token1
            return new_token

        return None

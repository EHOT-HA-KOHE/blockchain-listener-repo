from src.collectors.uniswap_v3_price_collector import UniswapV3PriceCollector


class EthUniswapV3PriceCollector(UniswapV3PriceCollector):
    network = 'ETH'
    eth_token_address = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
    abi_file_path = './abi/abi_eth_uniswap_v3.json'

    def __init__(
            self,
            wss_rpc: str,
            uniswap_v2_factory_address_str: str = '0x1F98431c8aD98523631AE4a59f267346ea31F984',
    ):
        super().__init__(
            wss_rpc,
            uniswap_v2_factory_address_str,
            self.network,
            self.eth_token_address,
            self.abi_file_path
        )

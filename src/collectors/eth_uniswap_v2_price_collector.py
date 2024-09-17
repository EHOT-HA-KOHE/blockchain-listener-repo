from src.collectors.uniswap_v2_price_collector import UniswapV2PriceCollector


class EthUniswapV2PriceCollector(UniswapV2PriceCollector):
    network = 'ETH'
    eth_token_address = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
    abi_file_path = './abi/abi_eth_uniswap_v2.json'

    def __init__(
            self,
            wss_rpc: str,
            uniswap_v2_factory_address_str: str = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
    ):
        super().__init__(
            wss_rpc,
            uniswap_v2_factory_address_str,
            self.network,
            self.eth_token_address,
            self.abi_file_path
        )

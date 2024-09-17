from src.collectors.uniswap_price_collector import UniswapPriceCollector
from src.collectors.uniswap_v2_price_collector import UniswapV2PriceCollector


class BaseUniswapV2PriceCollector(UniswapV2PriceCollector):
    network = 'BASE'
    base_token_address = '0x4200000000000000000000000000000000000006'
    abi_file_path = './abi/abi_base_uniswap_v2.json'

    def __init__(
            self,
            wss_rpc: str,
            uniswap_v2_factory_address_str: str = '0x8909Dc15e40173Ff4699343b6eB8132c65e18eC6',
    ):
        super().__init__(
            wss_rpc,
            uniswap_v2_factory_address_str,
            self.network,
            self.base_token_address,
            self.abi_file_path
        )

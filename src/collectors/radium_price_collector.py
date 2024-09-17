import asyncio

from websockets import ConnectionClosedError

from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction_status import EncodedConfirmedTransactionWithStatusMeta

from solana.rpc.api import Client
from solana.rpc.commitment import Commitment
from solana.exceptions import SolanaRpcException
from solana.rpc.websocket_api import connect, RpcTransactionLogsFilterMentions

from src.loguru_config import logger
from src.consts import SOL_MINT, OPEN_BOOK

from src.collectors.token_price_collector import TokenPriceCollector


class RadiumPriceCollector(TokenPriceCollector):
    dex_name = 'RADIUM'
    network = 'SOL'

    def __init__(
            self,
            sol_url='https://api.mainnet-beta.solana.com',
            wss_rpc='wss://api.mainnet-beta.solana.com',
    ):
        super().__init__()
        self.sol_url = sol_url
        self.wss_rpc = wss_rpc
        self.sol_client = Client(self.sol_url)

    def get_mint_from_signature(self, signature: str) -> str:
        transaction_data = self.get_transaction_by_sig(signature)
        token_mint = self.get_mint_from_transaction(transaction_data)
        return token_mint

    def get_transaction_by_sig(self, signature: str) -> EncodedConfirmedTransactionWithStatusMeta:
        tx_sig = Signature.from_string(signature)

        try:
            transaction_data = self.sol_client.get_transaction(
                tx_sig=tx_sig,
                commitment=Commitment("finalized"),
                max_supported_transaction_version=0
            )
        except SolanaRpcException as err:
            logger.error(err)
            transaction_data = None

        if transaction_data is None or not transaction_data.value:
            raise Exception(f'Transaction value is None! {transaction_data = }')

        return transaction_data.value

    def get_mint_from_transaction(self, transaction_data: EncodedConfirmedTransactionWithStatusMeta) -> str:
        account_keys: list = transaction_data.transaction.transaction.message.account_keys
        owner_account = str(account_keys[0])
        pre_token_balances = transaction_data.transaction.meta.pre_token_balances

        token_mint = None
        for balance in pre_token_balances:
            b_owner = str(balance.owner)
            b_mint = str(balance.mint)
            if b_owner == owner_account and b_mint != SOL_MINT:
                token_mint = b_mint

        return token_mint

    async def process_new_token_by_signature(self, signature: str):
        mint = self.get_mint_from_signature(signature)
        self.save_token(mint, self.dex_name, self.network)

    async def listen_new_tokens(self):
        while True:
            async with connect(self.wss_rpc) as websocket:
                await websocket.logs_subscribe(
                    filter_=RpcTransactionLogsFilterMentions(Pubkey.from_string(OPEN_BOOK)),
                    commitment=Commitment("finalized"),
                    # filters=[{'eventSignature': RADIUM_POOL_EVENT_SIG}]
                )
                while True:
                    try:
                        responses = await websocket.recv()
                        if 'InitializeInstruction' in str(responses):
                            sig = responses[0].result.value.signature
                            task = asyncio.create_task(self.process_new_token_by_signature(str(sig)))
                            logger.info(f'New listing signature: {sig}')
                    except ConnectionClosedError:
                        logger.error(f"=== CONNECTION CLOSED ===")
                        break
                    except Exception as e:
                        logger.error(f"Error: {e}")

import json
import os
import asyncio

from web3 import Web3


async def check_connection_and_listen(wss_rpc):
    try:
        web3 = Web3(Web3.WebsocketProvider(wss_rpc))

        if web3.is_connected():
            print("Successfully connected to Base network")

            # Пример прослушивания нового блока
            async def new_block_listener():
                while True:
                    block = web3.eth.get_block('latest')
                    print(f"New block received: {block['number']}")
                    await asyncio.sleep(10)

            await new_block_listener()
        else:
            print("Failed to connect to Base network")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    wss_rpc_base = os.getenv('BASE_WSS_RPC')  # Замените на ваш WSS URL
    asyncio.run(check_connection_and_listen(wss_rpc_base))

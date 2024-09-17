from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from src.env import PostgresEnv

connection_pool = pool.SimpleConnectionPool(1, 20, PostgresEnv().connect_str)


class PgUtils:

    def __enter__(self):
        self.connection = connection_pool.getconn()
        self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.connection.commit()
        connection_pool.putconn(self.connection)

    def get_token_by_address(self, token_address: str) -> dict:
        self.cursor.execute("SELECT * FROM tokens WHERE address = %s", (token_address,))
        result = self.cursor.fetchone()
        return result

    def store_token(
            self,
            name: str,
            symbol: str,
            address: str,
            creator: str,
            network: str,
            portal_url: str,
    ) -> None:
        query = """
        INSERT INTO tokens (symbol, name, address, creator, portal_url, network) 
        VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (address) DO NOTHING;
        """
        data = (symbol, name, address, creator, portal_url, network)
        self.cursor.execute(query, data)
        self.connection.commit()

    def update_token_portal_url(self, address: str, portal_url: str) -> None:
        query = "UPDATE tokens SET portal_url = %s WHERE address = %s;"
        data = (portal_url, address)
        self.cursor.execute(query, data)
        self.connection.commit()

    def store_token_price(
            self,
            token_id: int,
            price: float,
            native_liquidity: float,
            timestamp: int,
            dex_name: str
    ) -> None:
        query = """
        INSERT INTO token_prices (token_id, price, native_liquidity, timestamp, dex_name)
        VALUES (%s, %s, %s, %s, %s);
        """
        data = (token_id, price, native_liquidity, timestamp, dex_name)
        self.cursor.execute(query, data)
        self.connection.commit()

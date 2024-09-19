from datetime import datetime
import os

from dotenv import load_dotenv

from confluent_kafka import Producer

from src.loguru_config import logger


# Загрузка переменных окружения из .env файла
# load_dotenv('../.env')

# Получение адреса брокера из переменных окружения
# broker = os.getenv('KAFKA_BROKER', '127.0.0.1:9092')
broker = 'kafka:9092'

# Конфигурация Kafka Producer
producer = Producer({'bootstrap.servers': broker})


def save_add_alarm_about_new_pool_by_kafka(address: str, dex_name: str, network: str, created_at: str) -> None:
    # web_socket_topic = 'show-new-pool-ws'
    # save_to_db_topic = 'save-new-pool-to-db'

    # Формирование данных для отправки
    data = {
        "address": address,
        "dex_name": dex_name,
        "network": network,
        "created_at": created_at,
    }

    # Отправка данных в оба топика
    producer.produce('show-new-pool-ws', key='key', value=str(data))
    producer.produce('save-new-pool-to-db', key='key', value=str(data))

    # Отправка всех сообщений
    producer.flush()


if __name__ == '__main__':
    print('make_test_23097634')
    # save_add_alarm_about_new_pool_by_kafka('LOL_COIN', 'RADIUM', 'SOL')
    # save_add_alarm_about_new_pool_by_kafka('NOT_LOL_COIN', 'UNISWAP', 'BASE')

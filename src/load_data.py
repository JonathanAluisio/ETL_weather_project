from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

env_path = Path(__file__).parent.parent / 'config' / '.env'
load_dotenv(env_path)
 
user = os.getenv('ETL_DB_USER', os.getenv('DB_USER'))
password = os.getenv('ETL_DB_PASSWORD', os.getenv('DB_PASSWORD'))
database = os.getenv('ETL_DB_NAME', os.getenv('DB_NAME'))
host = os.getenv('ETL_DB_HOST', os.getenv('DB_HOST', 'postgres'))


def get_engine():
    return create_engine(
        f'postgresql+psycopg2://{user}:{quote_plus(password)}@{host}:5432/{database}'
    )


def load_weather_data(table_name: str, df):
    engine = get_engine()

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='append',
        index=False
    )
    logging.info('Dados carregados com sucesso!')

    df_check = pd.read_sql(f'SELECT * FROM {table_name}', con=engine)
    logging.info(f'Número de linhas na tabela {table_name}: {len(df_check)}')

import snowflake.connector
import pandas as pd
import streamlit as st


class SnowflakeConnection:
    def __init__(self, credentials):
        self.db_username = credentials['db_username']
        self.db_password = credentials['db_password']
        self.conn = self.init_connection()

    def init_connection(self):
        return snowflake.connector.connect(
            user = self.db_username,
            password = self.db_password,
            account = st.secrets["snowflake"]["account"],
            warehouse = st.secrets["snowflake"]["warehouse"],
            database = st.secrets["snowflake"]["database"],
            schema = st.secrets["snowflake"]["schema"],
            authenticator='externalbrowser')
    
    @st.experimental_memo(ttl = 600)
    def run_query(_self, query):
        with _self.conn.cursor() as cur:
            cur.execute(query)
            columns = [i[0] for i in cur.description]
            return pd.DataFrame(cur.fetchall(), columns=columns)
    
    @st.experimental_memo(ttl = 600)
    def fetchAndRunQuery(_self, query_filepath):
        file = open(query_filepath, 'r')
        query = file.read()
        file.close()
        df = _self.run_query(query)
        return df

import snowflake.connector
import pandas as pd
import streamlit as st


class SnowflakeConnection:
    def __init__(self):
        self.conn = self.init_connection()

    @st.cache_resource
    def init_connection(self):
        return snowflake.connector.connect(
            **st.secrets["snowflake"], client_session_keep_alive=True
        )

    # def run_query(self, query):
    #     with self.conn.cursor() as cur:
    #         cur.execute(query)
    #         return cur.fetchall()
    

    @st.experimental_memo(ttl=600)
    def run_query(_self, query):
        with _self.conn.cursor() as cur:
            cur.execute(query)
            columns = [i[0] for i in cur.description]
            return pd.DataFrame(cur.fetchall(), columns=columns)

    # @st.experimental_memo(ttl=600)
    # def fetchAndRunQuery(_self, query_filepath):
    #     file = open(query_filepath, 'r')
    #     query = file.read()
    #     file.close()
    #     df = _self.run_query(query)
    #     return df

from numpy import ones_like
import streamlit as st
# import numpy as np
import snowflake.connector

@st.cache_resource
def init_connection():
    return snowflake.connector.connect(
        **st.secrets["snowflake"], client_session_keep_alive=True
    )

@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Reviews Reporting",
        page_icon="🎯"
    )

    st.title("Reviews Reporting")
    conn = init_connection()




    




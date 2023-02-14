

import streamlit as st
import snowflake.connector
import pandas as pd

##################### Snowflake #####################
@st.cache_resource
def init_connection():
    return snowflake.connector.connect(
        **st.secrets["snowflake"], client_session_keep_alive=True
    )

@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        columns = [i[0] for i in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=columns)

conn = init_connection()

####################################################

success_query = '''
select b.business_id, b.name, count(distinct f.invocation_id) as "Successful Responses"
from "PROD_PLATFORM"."LOGS"."FUNCTION_INVOCATIONS" f
join "PROD_PLATFORM"."PUBLIC"."BUSINESSES" b on b.business_id = f.business_id
where function_name = 'reviewAutoRespond'
and invoke_duration_milliseconds > 10000
group by 1, 2
limit 10;
'''

success_df = run_query(success_query)
success_df



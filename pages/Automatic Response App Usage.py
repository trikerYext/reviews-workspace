

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

query = '''
with results as (
select f.business_id,
case 
    when invoke_duration_milliseconds >= 10000 then 'Auto-Response'
    when invoke_duration_milliseconds < 10000 then 'No Auto-Response'
end as "Result"
from "PROD_PLATFORM"."LOGS"."FUNCTION_INVOCATIONS" f
  where function_name = 'reviewAutoRespond'
)
select results.business_id, b.name, results."Result", count(results."Result")
from results
join "PROD_PLATFORM"."PUBLIC"."BUSINESSES" b on b.business_id = results.business_id
group by 1,2,3
order by 1;
'''

success_df = run_query(query)


success_df



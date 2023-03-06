
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

with st.expander("Show/Hide Report Inputs"):
    with st.form("Form"):

        business_id = st.text_input("Yext Business ID")

        form_submitted = st.form_submit_button("Run Report")

#business_id = 1269185
# Active Users Past 30d


def get_active_user_count(url_pattern):
    query = f'''
    select distinct user_id
    from prod_platform_local.public.storm_requests
    where business_id = {business_id}
    and date_trunc('day',date(storm_requests.request_timestamp)) >= DATEADD(DAY, -30, GETDATE())
    and url like '{url_pattern}'
    '''
    active_user_df = run_query(query)
    return len(active_user_df)


if form_submitted:  
    all_active_user_count = get_active_user_count('%')
    reviews_active_user_count = get_active_user_count('/s/%/reviews%')
    post_active_user_count = get_active_user_count('/s/%/social/post')
    listing_active_user_count = get_active_user_count('/s/%/listings%')
    search_active_user_count = get_active_user_count('/s/%/search%')
    analytics_active_user_count = get_active_user_count('/s/%/reports%')



    st.header('Distinct Active Users (Past 30d)')
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(label = 'All Pages', value = all_active_user_count )
        st.metric(label = 'Search', value = search_active_user_count )


    with c2:
        st.metric(label = 'Listings', value = listing_active_user_count )
        st.metric(label = 'Analytics', value = analytics_active_user_count )

    with c3:
        st.metric(label = 'Reviews', value = reviews_active_user_count )
        st.metric(label = 'Social', value = post_active_user_count )
    

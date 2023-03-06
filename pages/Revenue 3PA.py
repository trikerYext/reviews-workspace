import streamlit as st
import snowflake.connector
import pandas as pd
from datetime import datetime, date
from dateutil import rrule

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

st.title("3PA Revenue Dashboard")
t1, t2, t3 = st.tabs(["Overview", "Listings", "Reviews"])


def getGrowthDf(products):

    arrMoMQuery = f'''
        SELECT
        a."ADMIN_ID__C"  AS "ADMIN_ID",
        b.name ,
        spc."CURRENCYISOCODE" AS "CURRENCY",
        date_trunc('month',date(spc."ZUORA__EFFECTIVESTARTDATE__C")) as "START_DATE",
        date_trunc('month',date(spc."ZUORA__EFFECTIVEENDDATE__C")) as "END_DATE",
        TO_NUMBER(spc."ZUORA__QUANTITY__C", 38, 0) AS "QUANTITY",
        TO_NUMBER(spc."UNIT_MRR__C", 38, 2) AS "UNIT_MRR", 
        TO_NUMBER(spc."ZUORA__MONTHLYRECURRINGREVENUE__C", 38, 2) *  12 AS "PRODUCT_ACV_IN_CONTRACT"
        FROM "YEXT_SALESFORCE"."PUBLIC"."ZUORA__CUSTOMERACCOUNT__C" ca
        join "YEXT_SALESFORCE"."PUBLIC"."ZUORA__SUBSCRIPTIONPRODUCTCHARGE__C" spc on spc."ZUORA__ACCOUNT__C" = ca."ZUORA__ACCOUNT__C"
        join "YEXT_SALESFORCE"."PUBLIC"."ACCOUNT" a on a."YEXT_ZUORA_ACCOUNT_NUMBER__C" = CA."ZUORA__ACCOUNTNUMBER__C"
        join "PROD_PLATFORM"."PUBLIC"."BUSINESSES" b on b."BUSINESS_ID" = a."ADMIN_ID__C"
        WHERE 1
        and spc."UNIT_MRR__C" > 0
        and spc."ZUORA__PRODUCTNAME__C" in {products}
        order by 8 desc;
    '''
    df = run_query(arrMoMQuery)
    return df


test = getGrowthDf("('Review Monitoring','Review Response', 'Review Generation', 'Ultimate','Knowledge Engine: Ultimate (KE)')")
test
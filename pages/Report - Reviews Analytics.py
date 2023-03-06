import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
from wordcloud import WordCloud, STOPWORDS
import re
import matplotlib.pyplot as plt

st.set_option('deprecation.showPyplotGlobalUse', False)


with st.expander("Show/Hide Report Inputs"):
    with st.form("Form"):

        business_id = st.text_input("Yext Business ID")
        report_start_date = st.date_input("Report Start Date")
        report_end_date = st.date_input("Report End Date")
        publishers = st.multiselect('Publishers', [
                                    'Google Business Profile', 'Facebook', 'Yelp', 'TripAdvisor', 'Apple App Store', 'Google Play Store', 'First Party'],
                                    default=['Google Business Profile', 'Facebook', 'Yelp', 'TripAdvisor', 'Apple App Store', 'Google Play Store', 'First Party'])

        form_submitted = st.form_submit_button("Run Report")


if form_submitted:
    # st.write(business_id)
    df = pd.read_csv("hard_rock_reviews.csv")

    # L1 Values
    reviews_count = len(df)
    average_rating = df['Rating'].mean()
    reviews_without_response_count = len(df[df['Response'].isnull()])

    # L2 Values
    response_rate = (
        reviews_count - reviews_without_response_count)/reviews_count

    # Loop Through DF
    # Initialize list to store differences between review date & response date
    dif_list = []
    datetime_format = '%Y-%m-%d %I:%M %p'

    # Initialize string to store review words for wordcloud
    all_words = ""

    for index, row in df.iterrows():
        # If there is a response, calculate response time and add to dif_list
        if isinstance(row['Response'], str):
            review_datetime = datetime.strptime(
                row['Review Date'], datetime_format)
            response_datetime = datetime.strptime(
                row['Response Date'], datetime_format)
            # Calculate difference
            dif = response_datetime - review_datetime
            # Add to list of differences
            dif_list.append(dif)

        # If there is review content, save words for wordcloud
        if isinstance(row['Review'], str):
            review_content = row['Review']
            # Clean with regex
            review_content_cleaned_1 = re.sub('\t', "", review_content)
            review_content_cleaned_2 = re.split('\n', review_content_cleaned_1)
            review_content_cleaned_3 = "".join(review_content_cleaned_2)
            all_words += " " + review_content_cleaned_3

    # L2 - Average Response Time
    # Calculate average response time of the difference list
    avg_response_time = np.mean(dif_list)
    avg_response_time_seconds = avg_response_time.total_seconds()
    avg_response_time_hours = avg_response_time_seconds/3600

    # Wordcloud
    stopwords = set(STOPWORDS)
    wordcloud = WordCloud(background_color="white",
                          stopwords=stopwords).generate(all_words)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()

    # Hero Numbers
    st.header("Overview")

    col1, col2 = st.columns(2, gap='medium')
    col3, col4, col5 = st.columns(3)

    with col1:
        reviews_count_formatted = f"{reviews_count:,}"
        st.metric(label='Total Reviews', value=reviews_count_formatted)

    with col2:
        average_rating_rounded = round(average_rating, 2)
        st.metric(label='Average Rating', value=average_rating_rounded)

    with col3:
        reviews_without_response_formatted = f"{reviews_without_response_count:,}"
        st.metric(label='Reviews Awaiting Response',
                  value=reviews_without_response_formatted)

    with col4:

        response_rate_rounded = round(response_rate, 2)
        st.metric(label='Response Rate', value=response_rate_rounded)

    with col5:
        avg_response_time_hours_rounded = round(avg_response_time_hours, 2)
        st.metric(label='Average Response Time (Hours)',
                  value=avg_response_time_hours_rounded)

    # Display Wordcloud
    st.header("Wordcloud")
    st.pyplot()

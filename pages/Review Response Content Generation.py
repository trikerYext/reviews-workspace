import streamlit as st
import pandas as pd
import os
import openai
import csv


# Generic Model

# Trained Model

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["content_gen_pw"] == st.secrets["content_gen_pw"]:
            st.session_state["password_correct"] = True
            del st.session_state["content_gen_pw"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="content_gen_pw"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="content_gen_pw"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():


    st.header("Review Response Content Generation")
    t1, t2, t3 = st.tabs(
        ["Model Configuration", "Generate Single Response", "Generate Responses in Bulk"])

    openai.api_key = st.secrets['openai']['API_KEY']


    @st.cache_data
    def get_model_list():
        #models_response = openai.Model.list()

        # models = [x['id'] for x in models_response['data']]

        models = ['gpt-3.5-turbo', 'text-davinci-003', 'davinci', 'babbage', 'curie', 'ada']
        return models


    @st.cache_data
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')


    @st.cache_data
    def generate_response(review_content, review_reviewer_name, prompt, review_rating, model, max_tokens, temperature):
        prompt_with_inputs = prompt + f'''
        Author: {review_reviewer_name}
        Content: {review_content}
        Rating: {review_rating}
        '''

        if "turbo" in model:
            completion = openai.ChatCompletion.create(model=model, messages=[
                {"role": "user", "content": prompt_with_inputs}], temperature=temperature, max_tokens=max_tokens)
            response = completion.choices[0].message.content

        else:
            response = openai.Completion.create(
                model=model, prompt=prompt_with_inputs, temperature=temperature, max_tokens=max_tokens)['choices'][0]['text']

        return response


    with t1:
        with st.expander("Show/Hide Model Inputs"):
            prompt = st.text_area("Prompt", height=300, value='''
                You are a good support agent, responding to online reviews for a <TYPE OF BUSINESS>. You always respond in a concise and clear manner. Do not promise any refunds or specific action in response to a review.\n
                Respond to this review positively, using the following rules:\n
                Acknowledge the author by name\n
                Show a value statement\n
                Address the sentiment of the review\n
                Add a closing statement\n
                Response in the same language as the review\n
                ''')

            temperature = st.slider("Temperature", value=0.7)
            max_tokens = st.slider("Max Tokens", value=256)
            model = st.selectbox("Model", options=get_model_list())

    with t2:
        with st.form("Form"):

            review_rating = st.number_input("Rating", help='Review Rating', value=3.0,
                                            step=0.5, max_value=5.0, min_value=1.0)
            review_reviewer_name = st.text_input(
                "Reviewer Name", value="Jim Chapelle", help='Reviewer Name')
            review_content = st.text_area(
                "Review Content", value="I had a less than positive experience with the wait staff. Although we were the only customers present, our order came out incorrect. The risotto was delicious though.", help='Review Content', height=300)

            form_submitted = st.form_submit_button("Generate Response")

        if form_submitted:

            response = generate_response(review_content=review_content, review_reviewer_name=review_reviewer_name,
                                        review_rating=review_rating, model=model, prompt=prompt, max_tokens=max_tokens, temperature=temperature)


            st.write(response)

    with t3:

        uploaded_file = st.file_uploader(
            "Upload Review Export", help='You can download a file directly from the Review Monitoring or Review Response tabs in Storm and upload it here. Fields Required: Review, Rating, Author Name')

        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)

            if len(df.index) > 100:
                st.write("To limit costs, this tool is currently limited to generating 100 responses. Please submit a file with less reviews")

            else:
                with st.form("Bulk Form"):
                    submit_bulk = st.form_submit_button("Generate Responses")

                if submit_bulk:

                    output_df = pd.DataFrame()

                    for index, row in df.iterrows():
                        output_row = []
                        review_content = row['Review']
                        review_rating = row['Rating']
                        review_reviewer_name = row['Author Name']

                        response = generate_response(review_content=review_content, review_reviewer_name=review_reviewer_name,
                                                    review_rating=review_rating, model=model, prompt=prompt, max_tokens=max_tokens, temperature=temperature)

                        output_row = {
                            "Content": review_content,
                            "Rating": review_rating,
                            "Author": review_reviewer_name,
                            "Response": response
                        }
                        st.subheader("Review")
                        st.write("Author: " + review_reviewer_name)
                        st.write("Rating: " + str(review_rating))
                        if isinstance(review_content,str):
                            st.write("Content: " + review_content)
                        st.subheader("Response")
                        st.caption(response)
                        #st.write(output_row)

                        output_df = output_df.append(output_row, ignore_index=True)

                    csv = convert_df(output_df)

                    st.download_button(
                        label="Download Results",
                        data=csv,
                        file_name='generated_responses.csv',
                        mime='text/csv',
                    )

                    

import streamlit as st
import tweepy
from langchain.llms import OpenAI
from datetime import datetime
import json

if 'generated_content' not in st.session_state:
    st.session_state['generated_content'] = ""
if 'error_log' not in st.session_state:
    st.session_state.error_log = {'errors': []}

def log_error(error_message, location):
    error_info = {
        "error": error_message,
        "location": location,
        "timestamp": datetime.now().isoformat()
    }
    st.session_state.error_log['errors'].append(error_info)

def create_error_log_download_button():
    error_log_json = json.dumps(st.session_state.error_log, indent=2)
    st.download_button(
        label="Download Error Log",
        data=error_log_json,
        file_name="error_log.json",
        mime="application/json"
    )

BEARER_TOKEN = 'your_key_here'
CONSUMER_KEY = 'your_key_here'
CONSUMER_SECRET = 'your_key_here' 
ACCESS_TOKEN = 'your_key_here'
ACCESS_TOKEN_SECRET = 'your_key_here'

llm = OpenAI(api_key='your_key_here')

client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

user_credentials = {
    "testuser": "test",
    
}

def is_valid_user(username, password):
    return username in user_credentials and user_credentials[username] == password

def login_user(username, password):
    if is_valid_user(username, password):
        st.session_state['logged_in'] = True
    else:
        st.error("Access denied. Invalid username or password.")

def generate_content(topic):
    prompt = f"Write a tweet about {topic} at least 220 characters but shorter than 280 characters in a human like text"
    try:
        content = llm(prompt)
        if content:
            st.session_state['generated_content'] = content
            return content
        else:
            st.error("No content was generated. Please try again.")
    except Exception as e:
        error_message = str(e)
        log_error(error_message, 'generate_content')
        st.error("An error occurred while generating content.")
        return None

def post_to_twitter():
    tweet_text = st.session_state['generated_content']
    if tweet_text:
        try:
            response = client.create_tweet(text=tweet_text)
            if response:
                st.success("Posted to Twitter!")
                st.session_state['generated_content'] = "" 
            else:
                st.error("Failed to post to Twitter.")
        except Exception as e:
            error_message = str(e)
            log_error(error_message, 'post_to_twitter')
            st.error("An error occurred while posting to Twitter.")

st.title('Tweet-GPT')
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    user_username = st.text_input("Enter your username")
    user_password = st.text_input("Enter your password", type="password")
    if st.button("Login"):
        login_user(user_username, user_password)
else:
    st.sidebar.title('Navigation')
    page = st.sidebar.radio("Go to", ['Home', 'About the Project'])

    if page == 'Home':
        topic = st.text_input("What would you like to post about on Twitter?")
        if st.button("Generate Tweet"):
            if topic:
                generated_content = generate_content(topic)
                st.text_area("Generated Tweet", generated_content, height=150)
            else:
                st.error("Please enter a topic.")
        if st.button("Post to Twitter"):
            post_to_twitter()

    elif page == 'About the Project':
        st.write("About the Project: This project was made for marketing purposes. For test users, DM me on discord (ninjjaak) to apply for testing and gain access! Working on future changes!")

create_error_log_download_button()

import streamlit as st
from google_play_scraper import app, reviews
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import matplotlib.pyplot as plt

import nltk
nltk.download('punkt')
# Function to extract app ID from the URL
def extract_app_id(url):
    pattern = r'id=(?P<app_id>[a-zA-Z0-9._]+)'
    match = re.search(pattern, url)
    
    if match:
        app_id = match.group('app_id')
        return app_id
    else:
        return None

# Function to perform sentiment analysis
def perform_sentiment_analysis(text):
    stop = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    words = [w for w in words if w not in stop and len(w) >= 3]
    
    positive_words = open("positive.txt", "r", encoding='utf-8').read().split()
    negative_words = open("negative.txt", "r", encoding='utf-8').read().split()
    # fraud_words = open("fraud.txt", "r", encoding='utf-8').read().split()

    pos_count = sum(1 for w in words if w in positive_words)
    neg_count = sum(1 for w in words if w in negative_words)

    # for word in words:
    #     if word in fraud_words:
    #         return "fraud"

    if pos_count >= neg_count:
        return "positive"
    else:
        return "negative"

# Function to generate a pie chart
def generate_pie_chart(pos_percent, neg_percent):
    labels = ['Positive', 'Negative']
    sizes = [pos_percent, neg_percent]
    colors = ['#66b3ff', '#99ff99']
    
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    
    return fig1

# Streamlit App
def main():
    st.title("Fraud/ Faulty App Detection")

    # Input field for the app URL
    url = st.text_input("Enter App URL:")

    if st.button("Analyze"):
        # Extract app ID from the URL
        app_id = extract_app_id(url)

        if app_id:
            # Get app details
            try:
                app_info = app(app_id)
                app_name = app_info['title']
            except Exception as e:
                st.error(f"Error getting app details: {str(e)}")
                return

            # Scrape reviews
            try:
                reviews_list, _ = reviews(app_id, lang='en', country='us', sort='most_relevant', count=200)
            except Exception as e:
                st.error(f"Error getting reviews: {str(e)}")
                return

            # Perform sentiment analysis
            sentiment_results = [perform_sentiment_analysis(review['content']) for review in reviews_list]

            # Calculate percentages
            pos_percent = sentiment_results.count('positive') / len(sentiment_results) * 100
            neg_percent = sentiment_results.count('negative') / len(sentiment_results) * 100

            # Display results
            st.success(f"App Name: {app_name}")
            st.info(f"Positive Reviews Percent: {pos_percent:.2f}%")
            st.info(f"Negative Reviews Percent: {neg_percent:.2f}%")

            # Generate and display pie chart
            fig = generate_pie_chart(pos_percent, neg_percent)
            st.pyplot(fig)

            # Determine verdict
            if pos_percent >= neg_percent:
                st.success("Verdict: This is a good app!")
            else:
                st.error("Verdict: This is a Fraud/Faulty app!")

if __name__ == "__main__":
    main()

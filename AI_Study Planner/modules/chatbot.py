# chatbot.py
# Handles FAQ responses using TF-IDF similarity

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load chat dataset
chat_df = pd.read_csv("data/chat_cleaned.csv")

# Vectorize queries
vectorizer = TfidfVectorizer()
X_chat = vectorizer.fit_transform(chat_df['query'])

def chatbot_response(user_input):
    """
    Returns the most similar response from chat dataset
    """

    # Convert user question to vector
    user_vec = vectorizer.transform([user_input])

    # Calculate similarity
    similarity = cosine_similarity(user_vec, X_chat)

    # Get best match
    index = similarity.argmax()
    score = similarity[0][index]

    # If similarity too low → fallback
    if score < 0.3:
        return "I'm not sure. Try asking about assignments or study schedules."

    return chat_df.iloc[index]['response']
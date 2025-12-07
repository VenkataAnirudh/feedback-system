import os
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import streamlit as st

# Configure Gemini API


def configure_gemini(api_key):
    """Configure Gemini API with the provided key"""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')


# Data storage functions
DATA_FILE = "data/reviews.csv"


def ensure_data_directory():
    """Create data directory if it doesn't exist"""
    os.makedirs("data", exist_ok=True)


def load_reviews():
    """Load reviews from CSV file"""
    ensure_data_directory()
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return create_empty_dataframe()
    else:
        return create_empty_dataframe()


def create_empty_dataframe():
    """Create empty dataframe with required columns"""
    return pd.DataFrame(columns=[
        'timestamp', 'rating', 'review', 'ai_response',
        'ai_summary', 'recommended_actions'
    ])


def save_review(rating, review, ai_response, ai_summary, recommended_actions):
    """Save a new review to the CSV file"""
    ensure_data_directory()

    new_entry = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'rating': rating,
        'review': review,
        'ai_response': ai_response,
        'ai_summary': ai_summary,
        'recommended_actions': recommended_actions
    }

    df = load_reviews()
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    return True

# AI Generation Functions


def generate_user_response(model, rating, review):
    """Generate AI response for user dashboard"""
    prompt = f"""You are a customer service assistant. A customer has left the following review:

Rating: {rating} stars
Review: {review}

Generate a warm, empathetic, and professional response that:
1. Thanks them for their feedback
2. Addresses their specific concerns or praise
3. Is brief (2-3 sentences maximum)
4. Matches the tone to their rating (apologetic for low ratings, grateful for high ratings)

Response:"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Thank you for your {rating}-star review. We appreciate your feedback and will use it to improve our service."


def generate_admin_summary(model, rating, review):
    """Generate summary for admin dashboard"""
    prompt = f"""Summarize this customer review in ONE brief sentence (max 15 words):

Rating: {rating} stars
Review: {review}

Summary:"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"{rating}-star review: {review[:50]}..."


def generate_recommended_actions(model, rating, review):
    """Generate recommended actions for admin"""
    prompt = f"""Based on this customer review, suggest 2-3 specific, actionable next steps for the business:

Rating: {rating} stars
Review: {review}

Provide recommendations as a brief bulleted list. Be specific and practical.

Recommendations:"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        if rating <= 2:
            return "• Contact customer immediately\n• Investigate issue\n• Offer compensation"
        elif rating == 3:
            return "• Follow up with customer\n• Identify improvement areas\n• Monitor similar feedback"
        else:
            return "• Thank customer\n• Share positive feedback with team\n• Encourage public review"


def get_sentiment_color(rating):
    """Return color based on rating"""
    if rating <= 2:
        return "#ff4444"  # Red
    elif rating == 3:
        return "#ffaa00"  # Orange
    else:
        return "#44ff44"  # Green


def get_rating_emoji(rating):
    """Return emoji based on rating"""
    emojis = {1: "😞", 2: "😕", 3: "😐", 4: "😊", 5: "🤩"}
    return emojis.get(rating, "⭐")

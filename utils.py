import os
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import streamlit as st
import json

# Use session state for data storage since we can't write to CSV on Streamlit Cloud
DATA_FILE = "data/reviews.csv"

def ensure_data_directory():
    """Create data directory if it doesn't exist"""
    os.makedirs("data", exist_ok=True)

def init_session_storage():
    """Initialize session state for storing reviews"""
    if 'reviews_data' not in st.session_state:
        st.session_state.reviews_data = load_reviews_from_csv()

def load_reviews_from_csv():
    """Load existing reviews from CSV"""
    ensure_data_directory()
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if len(df) > 0 and 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except:
            return create_empty_dataframe()
    return create_empty_dataframe()

def create_empty_dataframe():
    """Create empty dataframe"""
    return pd.DataFrame(columns=[
        'timestamp', 'rating', 'review', 'ai_response', 
        'ai_summary', 'recommended_actions'
    ])

def load_reviews():
    """Load reviews from session state"""
    init_session_storage()
    return st.session_state.reviews_data

def save_review(rating, review, ai_response="", ai_summary="", recommended_actions=""):
    """Save review to session state (will be processed by admin)"""
    init_session_storage()
    
    new_entry = {
        'timestamp': datetime.now(),
        'rating': int(rating),
        'review': str(review),
        'ai_response': str(ai_response),
        'ai_summary': str(ai_summary),
        'recommended_actions': str(recommended_actions)
    }
    
    new_df = pd.DataFrame([new_entry])
    st.session_state.reviews_data = pd.concat(
        [st.session_state.reviews_data, new_df], 
        ignore_index=True
    )
    
    return True

def configure_gemini_api(api_key):
    """Configure Gemini API for admin use"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        # Quick test
        response = model.generate_content("Say OK")
        if response.text:
            return model
        return None
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

def generate_all_ai_content(model, rating, review):
    """Generate all AI content at once (called from admin)"""
    try:
        # Generate user response
        user_prompt = f"""You are a customer service representative. Write a warm, empathetic response to this review:

Rating: {rating}/5 stars
Review: {review}

Keep it 2-3 sentences. Match tone to rating (apologetic for low, grateful for high).

Response:"""
        
        user_response = model.generate_content(user_prompt).text.strip()
        
        # Generate summary
        summary_prompt = f"""Summarize this review in ONE brief sentence (max 15 words):

Rating: {rating}/5
Review: {review}

Summary:"""
        
        summary = model.generate_content(summary_prompt).text.strip()
        
        # Generate actions
        actions_prompt = f"""Provide 3 specific, actionable recommendations based on this feedback:

Rating: {rating}/5
Review: {review}

Format as numbered list (1., 2., 3.). Be specific and practical.

Recommendations:"""
        
        actions = model.generate_content(actions_prompt).text.strip()
        
        return {
            'ai_response': user_response,
            'ai_summary': summary,
            'recommended_actions': actions
        }
        
    except Exception as e:
        # Fallback responses
        if rating <= 2:
            return {
                'ai_response': "We sincerely apologize for your experience. Your feedback is invaluable and we're taking immediate action to address these concerns.",
                'ai_summary': f"{rating}★ - Customer dissatisfied with service",
                'recommended_actions': "1. Contact customer within 24 hours\n2. Investigate issues raised\n3. Offer compensation and follow up"
            }
        elif rating == 3:
            return {
                'ai_response': "Thank you for your honest feedback. We appreciate your input and are always looking to improve your experience.",
                'ai_summary': f"{rating}★ - Neutral feedback on service",
                'recommended_actions': "1. Follow up for more details\n2. Review relevant processes\n3. Monitor for similar feedback"
            }
        else:
            return {
                'ai_response': f"Thank you so much for your wonderful {rating}-star review! We're thrilled you had a great experience with us!",
                'ai_summary': f"{rating}★ - Customer very satisfied",
                'recommended_actions': "1. Thank customer personally\n2. Share feedback with team\n3. Request testimonial"
            }

def update_review_with_ai(index, ai_response, ai_summary, recommended_actions):
    """Update a review with AI-generated content"""
    init_session_storage()
    st.session_state.reviews_data.loc[index, 'ai_response'] = ai_response
    st.session_state.reviews_data.loc[index, 'ai_summary'] = ai_summary
    st.session_state.reviews_data.loc[index, 'recommended_actions'] = recommended_actions

def get_sentiment_color(rating):
    """Return color based on rating"""
    colors = {1: "#D32F2F", 2: "#F57C00", 3: "#FBC02D", 4: "#7CB342", 5: "#388E3C"}
    return colors.get(rating, "#757575")

def get_sentiment_bg_color(rating):
    """Return background color based on rating"""
    colors = {1: "#FFEBEE", 2: "#FFF3E0", 3: "#FFFDE7", 4: "#F1F8E9", 5: "#E8F5E9"}
    return colors.get(rating, "#F5F5F5")

def get_rating_emoji(rating):
    """Return emoji for rating"""
    emojis = {1: "😞", 2: "😕", 3: "😐", 4: "😊", 5: "🤩"}
    return emojis.get(rating, "⭐")

def get_rating_text(rating):
    """Return text for rating"""
    texts = {1: "Very Dissatisfied", 2: "Dissatisfied", 3: "Neutral", 4: "Satisfied", 5: "Very Satisfied"}
    return texts.get(rating, "Unknown")

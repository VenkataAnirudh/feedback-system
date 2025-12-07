import os
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import streamlit as st

# Data storage
DATA_FILE = "data/reviews.csv"

def ensure_data_directory():
    """Create data directory if it doesn't exist"""
    os.makedirs("data", exist_ok=True)

def configure_gemini_api(api_key):
    """Configure Gemini API and return model"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        # Test the connection
        test_response = model.generate_content("Say 'OK' if you can hear me")
        if test_response.text:
            return model
        return None
    except Exception as e:
        st.error(f"API Configuration Error: {str(e)}")
        return None

def load_reviews():
    """Load reviews from CSV file"""
    ensure_data_directory()
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if 'timestamp' in df.columns and len(df) > 0:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            st.error(f"Error loading reviews: {str(e)}")
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
    """Save a new review to CSV file"""
    ensure_data_directory()
    
    try:
        new_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'rating': int(rating),
            'review': str(review),
            'ai_response': str(ai_response),
            'ai_summary': str(ai_summary),
            'recommended_actions': str(recommended_actions)
        }
        
        df = load_reviews()
        new_df = pd.DataFrame([new_entry])
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        
        return True
    except Exception as e:
        st.error(f"Error saving review: {str(e)}")
        return False

def generate_user_response(model, rating, review):
    """Generate personalized AI response for customer"""
    
    prompt = f"""You are a professional customer service representative. Generate a warm, personalized response to this customer review.

Customer Rating: {rating} out of 5 stars
Customer Review: {review}

Instructions:
- Be warm, empathetic, and genuine
- Address their specific feedback
- Keep it 2-3 sentences maximum
- For ratings 1-2: Apologize sincerely and show commitment to improve
- For rating 3: Thank them and express desire to do better
- For ratings 4-5: Show genuine appreciation and gratitude

Write ONLY the response text (no labels, no formatting):"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # Fallback responses based on rating
        fallback = {
            1: "We sincerely apologize for your experience. Your feedback is crucial to us, and we're taking immediate action to address these concerns. Thank you for bringing this to our attention.",
            2: "We're truly sorry we didn't meet your expectations. We value your feedback and are committed to making significant improvements. Please give us another chance to serve you better.",
            3: "Thank you for your honest feedback. We appreciate you taking the time to share your thoughts, and we're always looking for ways to enhance your experience.",
            4: "Thank you so much for your positive review! We're delighted that you had a great experience with us. Your support means a lot to our team!",
            5: "Wow, thank you for the amazing 5-star review! We're thrilled that we exceeded your expectations. We look forward to continuing to serve you with excellence!"
        }
        return fallback.get(rating, "Thank you for your feedback. We truly appreciate you taking the time to share your experience with us.")

def generate_admin_summary(model, rating, review):
    """Generate brief summary for admin dashboard"""
    
    prompt = f"""Summarize this customer review in ONE concise sentence (maximum 15 words).

Rating: {rating}/5 stars
Review: {review}

Focus on the main point. Be specific and brief.

Summary:"""
    
    try:
        response = model.generate_content(prompt)
        summary = response.text.strip()
        # Limit length
        if len(summary) > 120:
            summary = summary[:117] + "..."
        return summary
    except Exception as e:
        # Fallback summary
        truncated = review[:80] + "..." if len(review) > 80 else review
        return f"{rating}★ review: {truncated}"

def generate_recommended_actions(model, rating, review):
    """Generate actionable recommendations for business"""
    
    prompt = f"""As a business consultant, provide 3 SPECIFIC, ACTIONABLE recommendations based on this customer feedback.

Rating: {rating}/5 stars
Review: {review}

Format as a numbered list (1., 2., 3.). Each recommendation must be:
- Specific to THIS feedback
- Immediately actionable
- Practical for business implementation
- Professional and clear

Recommendations:"""
    
    try:
        response = model.generate_content(prompt)
        actions = response.text.strip()
        return actions
    except Exception as e:
        # Smart fallback based on rating
        if rating <= 2:
            return """1. Contact customer within 24 hours to personally address their concerns
2. Conduct internal review of the issues raised and implement corrective measures
3. Offer appropriate compensation and schedule follow-up to ensure satisfaction"""
        elif rating == 3:
            return """1. Reach out to customer for detailed feedback on improvement areas
2. Review and optimize processes related to their experience
3. Monitor future interactions to ensure consistent quality improvement"""
        else:
            return """1. Send personal thank you note and share positive feedback with entire team
2. Request permission to use as testimonial in marketing materials
3. Identify successful practices from this interaction and standardize them"""

def get_sentiment_color(rating):
    """Return color code based on rating"""
    colors = {
        1: "#D32F2F",  # Deep Red
        2: "#F57C00",  # Orange  
        3: "#FBC02D",  # Yellow
        4: "#7CB342",  # Light Green
        5: "#388E3C"   # Dark Green
    }
    return colors.get(rating, "#757575")

def get_sentiment_bg_color(rating):
    """Return background color based on rating"""
    colors = {
        1: "#FFEBEE",  # Light Red
        2: "#FFF3E0",  # Light Orange
        3: "#FFFDE7",  # Light Yellow
        4: "#F1F8E9",  # Light Green
        5: "#E8F5E9"   # Lighter Green
    }
    return colors.get(rating, "#F5F5F5")

def get_rating_emoji(rating):
    """Return emoji for rating"""
    emojis = {
        1: "😞",
        2: "😕", 
        3: "😐",
        4: "😊",
        5: "🤩"
    }
    return emojis.get(rating, "⭐")

def get_rating_text(rating):
    """Return text description for rating"""
    texts = {
        1: "Very Dissatisfied",
        2: "Dissatisfied",
        3: "Neutral", 
        4: "Satisfied",
        5: "Very Satisfied"
    }
    return texts.get(rating, "Unknown")

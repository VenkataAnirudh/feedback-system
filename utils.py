import pandas as pd
import google.generativeai as genai
from datetime import datetime
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets Setup
def get_google_sheet():
    """Connect to Google Sheets"""
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        sheet_url = st.secrets["SHEET_URL"]
        sheet = client.open_by_url(sheet_url)
        worksheet = sheet.sheet1
        
        return worksheet
    except Exception as e:
        st.error(f"Google Sheets connection error: {str(e)}")
        return None

def load_reviews():
    """Load reviews from Google Sheets"""
    try:
        worksheet = get_google_sheet()
        if worksheet is None:
            return pd.DataFrame(columns=['timestamp', 'rating', 'review', 'ai_response', 'ai_summary', 'recommended_actions'])
        
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        if len(df) > 0 and 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    except Exception as e:
        st.error(f"Load error: {str(e)}")
        return pd.DataFrame(columns=['timestamp', 'rating', 'review', 'ai_response', 'ai_summary', 'recommended_actions'])

def save_review(rating, review):
    """Save new review to Google Sheets"""
    try:
        worksheet = get_google_sheet()
        if worksheet is None:
            return False
        
        new_row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            int(rating),
            str(review),
            "",  # ai_response - empty initially
            "",  # ai_summary - empty initially
            ""   # recommended_actions - empty initially
        ]
        
        worksheet.append_row(new_row)
        return True
    except Exception as e:
        st.error(f"Save error: {str(e)}")
        return False

def update_review_with_ai(row_number, ai_response, ai_summary, recommended_actions):
    """Update a review with AI content"""
    try:
        worksheet = get_google_sheet()
        if worksheet is None:
            return False
        
        # row_number is 0-indexed in dataframe, but sheets is 1-indexed + header row
        sheet_row = row_number + 2
        
        worksheet.update_cell(sheet_row, 4, ai_response)  # Column D
        worksheet.update_cell(sheet_row, 5, ai_summary)   # Column E
        worksheet.update_cell(sheet_row, 6, recommended_actions)  # Column F
        
        return True
    except Exception as e:
        st.error(f"Update error: {str(e)}")
        return False

def configure_gemini_api(api_key):
    """Configure Gemini API"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say OK")
        if response.text:
            return model
        return None
    except Exception as e:
        return None

def generate_all_ai_content(model, rating, review):
    """Generate all AI content at once"""
    try:
        # User response
        user_prompt = f"""Write a brief, empathetic customer service response (2-3 sentences) to this review:

Rating: {rating}/5 stars
Review: {review}

Response:"""
        
        user_response = model.generate_content(user_prompt).text.strip()
        
        # Summary
        summary_prompt = f"""Summarize in ONE sentence (max 12 words):
Rating: {rating}/5
Review: {review}
Summary:"""
        
        summary = model.generate_content(summary_prompt).text.strip()
        
        # Actions
        actions_prompt = f"""List 3 specific actions based on this feedback:
Rating: {rating}/5
Review: {review}
Actions (numbered 1,2,3):"""
        
        actions = model.generate_content(actions_prompt).text.strip()
        
        return {
            'ai_response': user_response,
            'ai_summary': summary,
            'recommended_actions': actions
        }
        
    except:
        # Fallback
        if rating <= 2:
            return {
                'ai_response': "We sincerely apologize. Your feedback is invaluable and we're taking immediate action.",
                'ai_summary': f"{rating}★ - Customer dissatisfied",
                'recommended_actions': "1. Contact customer ASAP\n2. Investigate issue\n3. Offer resolution"
            }
        elif rating == 3:
            return {
                'ai_response': "Thank you for your feedback. We're always working to improve your experience.",
                'ai_summary': f"{rating}★ - Neutral feedback",
                'recommended_actions': "1. Follow up with customer\n2. Review processes\n3. Monitor feedback"
            }
        else:
            return {
                'ai_response': f"Thank you for the {rating}-star review! We're thrilled you had a great experience!",
                'ai_summary': f"{rating}★ - Very satisfied",
                'recommended_actions': "1. Thank customer\n2. Share with team\n3. Request testimonial"
            }

def get_sentiment_color(rating):
    colors = {1: "#D32F2F", 2: "#F57C00", 3: "#FBC02D", 4: "#7CB342", 5: "#388E3C"}
    return colors.get(rating, "#757575")

def get_rating_emoji(rating):
    emojis = {1: "😞", 2: "😕", 3: "😐", 4: "😊", 5: "🤩"}
    return emojis.get(rating, "⭐")

def get_rating_text(rating):
    texts = {1: "Very Dissatisfied", 2: "Dissatisfied", 3: "Neutral", 4: "Satisfied", 5: "Very Satisfied"}
    return texts.get(rating, "Unknown")

def time_ago(timestamp):
    """Calculate time ago"""
    try:
        now = datetime.now()
        diff = now - pd.to_datetime(timestamp)
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            mins = int(seconds / 60)
            return f"{mins}m ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}h ago"
        else:
            days = int(seconds / 86400)
            return f"{days}d ago"
    except:
        return ""

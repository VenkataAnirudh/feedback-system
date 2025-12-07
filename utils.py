import pandas as pd
import google.generativeai as genai
from datetime import datetime
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_google_sheet():
    """Connect to Google Sheets with detailed error handling"""
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        sheet_url = st.secrets["SHEET_URL"]
        sheet = client.open_by_url(sheet_url)
        worksheet = sheet.sheet1
        
        headers = worksheet.row_values(1)
        expected = ['timestamp', 'rating', 'review', 'ai_response', 'ai_summary', 'recommended_actions']
        
        if not headers:
            worksheet.append_row(expected)
            st.success("✅ Initialized Google Sheet headers")
        
        return worksheet
    except KeyError as e:
        st.error(f"❌ Missing secret: {str(e)}")
        return None
    except gspread.exceptions.SpreadsheetNotFound:
        st.error("❌ Google Sheet not found. Check SHEET_URL")
        return None
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")
        return None

def load_reviews():
    """Load all reviews from Google Sheets"""
    try:
        worksheet = get_google_sheet()
        if worksheet is None:
            return pd.DataFrame(columns=['timestamp', 'rating', 'review', 'ai_response', 'ai_summary', 'recommended_actions'])
        
        data = worksheet.get_all_records()
        
        if not data:
            return pd.DataFrame(columns=['timestamp', 'rating', 'review', 'ai_response', 'ai_summary', 'recommended_actions'])
        
        df = pd.DataFrame(data)
        
        required_cols = ['timestamp', 'rating', 'review', 'ai_response', 'ai_summary', 'recommended_actions']
        for col in required_cols:
            if col not in df.columns:
                df[col] = ''
        
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=['timestamp'])
        
        df = df.fillna('')
        
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(3).astype(int)
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error loading reviews: {str(e)}")
        return pd.DataFrame(columns=['timestamp', 'rating', 'review', 'ai_response', 'ai_summary', 'recommended_actions'])

def save_review(rating, review):
    """Save new review to Google Sheets"""
    try:
        worksheet = get_google_sheet()
        if worksheet is None:
            st.error("❌ Cannot connect to Google Sheet")
            return False
        
        new_row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            int(rating),
            str(review),
            "",
            "",
            ""
        ]
        
        worksheet.append_row(new_row)
        return True
        
    except Exception as e:
        st.error(f"❌ Save error: {str(e)}")
        return False

def update_review_with_ai(row_index, ai_response, ai_summary, recommended_actions):
    """Update a specific review row with AI-generated content"""
    try:
        worksheet = get_google_sheet()
        if worksheet is None:
            return False
        
        sheet_row = row_index + 2
        
        worksheet.update_cell(sheet_row, 4, str(ai_response))
        worksheet.update_cell(sheet_row, 5, str(ai_summary))
        worksheet.update_cell(sheet_row, 6, str(recommended_actions))
        
        return True
        
    except Exception as e:
        st.error(f"❌ Update error: {str(e)}")
        return False

def configure_gemini_api(api_key):
    """Configure and test Gemini API connection"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        response = model.generate_content("Say OK")
        if response.text:
            return model
        return None
        
    except Exception as e:
        st.error(f"❌ Gemini API Error: {str(e)}")
        return None

def generate_all_ai_content(model, rating, review):
    """Generate AI response, summary, and recommended actions"""
    try:
        user_prompt = f"""You are a professional customer service representative. Write a brief, empathetic response (2-3 sentences) to this customer review:

Rating: {rating}/5 stars
Review: {review}

Generate a professional response that:
- Thanks the customer for their feedback
- Addresses their sentiment appropriately
- Is warm and genuine

Response:"""
        
        user_response = model.generate_content(user_prompt).text.strip()
        
        summary_prompt = f"""Summarize this review in ONE concise sentence (maximum 12 words):

Rating: {rating}/5
Review: {review}

Summary:"""
        
        summary = model.generate_content(summary_prompt).text.strip()
        
        actions_prompt = f"""Based on this customer feedback, suggest 3 specific, actionable steps the business should take. Format as a numbered list.

Rating: {rating}/5 stars
Review: {review}

Provide 3 concrete action items:"""
        
        actions = model.generate_content(actions_prompt).text.strip()
        
        return {
            'ai_response': user_response,
            'ai_summary': summary,
            'recommended_actions': actions
        }
        
    except Exception as e:
        st.warning(f"⚠️ AI generation failed: {str(e)}")
        
        if rating <= 2:
            return {
                'ai_response': "We sincerely apologize for your experience. Your feedback is invaluable and we're committed to making this right. Our team will reach out to you shortly.",
                'ai_summary': f"{rating}★ - Customer reported negative experience",
                'recommended_actions': "1. Contact customer immediately to apologize and understand issue\n2. Investigate root cause of the problem\n3. Implement corrective measures to prevent recurrence"
            }
        elif rating == 3:
            return {
                'ai_response': "Thank you for your feedback. We appreciate you taking the time to share your experience. We're always working to improve and your input helps us do that.",
                'ai_summary': f"{rating}★ - Mixed feedback with room for improvement",
                'recommended_actions': "1. Follow up with customer to understand specific concerns\n2. Review internal processes related to feedback\n3. Monitor similar feedback patterns"
            }
        else:
            return {
                'ai_response': f"Thank you so much for the wonderful {rating}-star review! We're thrilled that you had a great experience with us. We look forward to serving you again!",
                'ai_summary': f"{rating}★ - Highly satisfied customer",
                'recommended_actions': "1. Thank the customer personally if possible\n2. Share positive feedback with the team\n3. Request permission to use as testimonial"
            }

def get_sentiment_color(rating):
    """Return color based on rating sentiment"""
    colors = {
        1: "#D32F2F",
        2: "#F57C00",
        3: "#FBC02D",
        4: "#7CB342",
        5: "#388E3C"
    }
    return colors.get(rating, "#757575")

def get_rating_emoji(rating):
    """Return emoji based on rating"""
    emojis = {
        1: "😞",
        2: "😕",
        3: "😐",
        4: "😊",
        5: "🤩"
    }
    return emojis.get(rating, "⭐")

def get_rating_text(rating):
    """Return text description based on rating"""
    texts = {
        1: "Very Dissatisfied",
        2: "Dissatisfied",
        3: "Neutral",
        4: "Satisfied",
        5: "Very Satisfied"
    }
    return texts.get(rating, "Unknown")

def time_ago(timestamp):
    """Calculate and return human-readable time difference"""
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
        return "Unknown"

def check_if_ai_processed(row):
    """Check if a review row has been processed by AI - SAFE ACCESS"""
    try:
        if 'ai_response' not in row:
            return False
        ai_response = str(row['ai_response']).strip()
        return len(ai_response) > 0
    except:
        return False

def safe_get_value(row, key, default=''):
    """Safely get value from row with fallback"""
    try:
        if key not in row:
            return default
        value = row[key]
        if pd.isna(value) or value is None:
            return default
        return str(value).strip()
    except:
        return default

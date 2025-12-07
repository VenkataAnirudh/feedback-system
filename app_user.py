import streamlit as st
from utils import save_review, get_rating_emoji, get_rating_text, get_sentiment_color

st.set_page_config(page_title="Customer Feedback", page_icon="⭐", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.main { padding: 2rem 1rem; max-width: 800px; margin: 0 auto; background: #f8f9fa; }
.header-container {
    text-align: center; padding: 3rem 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px; margin-bottom: 2rem; color: white;
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
}
.header-title { font-size: 2.8rem; font-weight: 700; margin-bottom: 0.5rem; }
.header-subtitle { font-size: 1.2rem; opacity: 0.95; }
.rating-container {
    background: white; border-radius: 20px; padding: 2.5rem;
    text-align: center; margin: 2rem 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1); border-left: 6px solid;
}
.rating-emoji { font-size: 5rem; margin: 1rem 0; }
.rating-text { font-size: 2rem; font-weight: 700; margin: 0.5rem 0; }
.rating-label { font-size: 1rem; color: #666; text-transform: uppercase; letter-spacing: 2px; }
.stTextArea textarea {
    border-radius: 15px; border: 2px solid #e0e0e0;
    padding: 1.2rem; font-size: 1.05rem; background: white;
}
.stButton>button {
    width: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white; padding: 1.2rem 2rem; font-size: 1.3rem;
    font-weight: 600; border-radius: 15px; border: none; margin-top: 1.5rem;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}
.success-box {
    background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
    border-radius: 20px; padding: 2.5rem; margin: 2rem 0;
    box-shadow: 0 10px 40px rgba(132, 250, 176, 0.3);
}
.success-title { font-size: 2rem; font-weight: 700; color: #2c3e50; margin-bottom: 1rem; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <div class="header-title">⭐ Customer Feedback Portal</div>
    <div class="header-subtitle">Your voice matters! Share your experience</div>
</div>
""", unsafe_allow_html=True)

if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'current_rating' not in st.session_state:
    st.session_state.current_rating = 3

if not st.session_state.submitted:
    st.markdown("### 📊 Rate Your Experience")
    
    rating = st.slider("Drag to rate", 1, 5, st.session_state.current_rating)
    st.session_state.current_rating = rating
    
    emoji = get_rating_emoji(rating)
    rating_text = get_rating_text(rating)
    color = get_sentiment_color(rating)
    
    st.markdown(f"""
    <div class="rating-container" style="border-left-color: {color};">
        <div class="rating-emoji">{emoji}</div>
        <div class="rating-text" style="color: {color};">{rating} Stars</div>
        <div class="rating-label">{rating_text}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ✍️ Your Feedback")
    review = st.text_area("", height=180, placeholder="Share your thoughts...")
    
    char_count = len(review.strip())
    if char_count < 10:
        st.caption(f"✏️ {char_count}/10 characters")
    else:
        st.caption(f"✅ {char_count} characters")
    
    if st.button("🚀 Submit Feedback"):
        if char_count < 10:
            st.error("❌ Minimum 10 characters required")
        else:
            with st.spinner("Submitting..."):
                if save_review(rating, review):
                    st.session_state.submitted = True
                    st.session_state.saved_rating = rating
                    st.rerun()
                else:
                    st.error("❌ Submission failed. Please try again.")

else:
    st.markdown("""
    <div class="success-box">
        <div class="success-title">✅ Thank You!</div>
        <p style="font-size: 1.15rem; color: #2c3e50;">
            Your feedback has been received. Our team will review it shortly!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.get('saved_rating', 3) >= 4:
        st.balloons()
    
    if st.button("📝 Submit Another", type="primary", use_container_width=True):
        st.session_state.submitted = False
        st.session_state.current_rating = 3
        st.rerun()

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #95a5a6; padding: 2rem 0;'>
    <p style='margin: 0;'>🤖 AI-Powered Feedback System</p>
</div>
""", unsafe_allow_html=True)


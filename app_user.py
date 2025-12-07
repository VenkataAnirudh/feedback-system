import streamlit as st
from utils import (
    save_review,
    get_rating_emoji,
    get_rating_text,
    get_sentiment_color,
    init_session_storage
)

# Page config
st.set_page_config(
    page_title="Customer Feedback Portal",
    page_icon="⭐",
    layout="centered"
)

# Initialize storage
init_session_storage()

# Professional CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.main { 
    padding: 2rem 1rem; 
    max-width: 800px; 
    margin: 0 auto; 
    background: #f8f9fa; 
}

.header-container {
    text-align: center;
    padding: 3rem 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    margin-bottom: 2rem;
    color: white;
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
}

.header-title {
    font-size: 2.8rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.header-subtitle {
    font-size: 1.2rem;
    opacity: 0.95;
}

.rating-container {
    background: white;
    border-radius: 20px;
    padding: 2.5rem;
    text-align: center;
    margin: 2rem 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    border-left: 6px solid;
    transition: all 0.3s ease;
}

.rating-emoji {
    font-size: 5rem;
    margin: 1rem 0;
    animation: bounce 0.6s ease;
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-15px); }
}

.rating-text {
    font-size: 2rem;
    font-weight: 700;
    margin: 0.5rem 0;
}

.rating-label {
    font-size: 1rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.stTextArea textarea {
    border-radius: 15px;
    border: 2px solid #e0e0e0;
    padding: 1.2rem;
    font-size: 1.05rem;
    background: white;
    transition: all 0.3s ease;
}

.stTextArea textarea:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.stButton>button {
    width: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.2rem 2rem;
    font-size: 1.3rem;
    font-weight: 600;
    border-radius: 15px;
    border: none;
    margin-top: 1.5rem;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    transition: all 0.3s ease;
}

.stButton>button:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(102, 126, 234, 0.6);
}

.success-box {
    background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
    border-radius: 20px;
    padding: 2.5rem;
    margin: 2rem 0;
    box-shadow: 0 10px 40px rgba(132, 250, 176, 0.3);
    animation: slideIn 0.6s ease;
}

@keyframes slideIn {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

.success-title {
    font-size: 2rem;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 1rem;
}

.info-box {
    background: #e3f2fd;
    border-left: 4px solid #2196F3;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1.5rem 0;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-container">
    <div class="header-title">⭐ Customer Feedback Portal</div>
    <div class="header-subtitle">Your voice matters! Share your experience with us</div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'current_rating' not in st.session_state:
    st.session_state.current_rating = 3

# Main Form
if not st.session_state.submitted:
    
    st.markdown("### 📊 Rate Your Experience")
    
    # Rating slider
    rating = st.slider(
        "Drag to rate your experience",
        min_value=1,
        max_value=5,
        value=st.session_state.current_rating,
        help="1 = Poor, 5 = Excellent"
    )
    
    # Update session state
    st.session_state.current_rating = rating
    
    # DYNAMIC rating display - updates as you drag
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
    
    st.markdown("### ✍️ Tell Us More")
    
    review = st.text_area(
        "Your detailed feedback",
        height=180,
        placeholder="What did you like? What could we improve? Share your thoughts...",
        help="Minimum 10 characters required"
    )
    
    # Character counter
    char_count = len(review.strip())
    if char_count < 10:
        st.caption(f"✏️ {char_count}/10 characters (minimum required)")
    else:
        st.caption(f"✅ {char_count} characters")
    
    # Submit button
    if st.button("🚀 Submit Your Feedback", use_container_width=True):
        if char_count < 10:
            st.error("❌ Please write at least 10 characters in your review.")
        else:
            # Save review WITHOUT AI content (admin will add it later)
            success = save_review(
                rating=rating,
                review=review,
                ai_response="",  # Will be filled by admin
                ai_summary="",
                recommended_actions=""
            )
            
            if success:
                st.session_state.submitted = True
                st.session_state.saved_rating = rating
                st.rerun()
            else:
                st.error("❌ Failed to save review. Please try again.")

# Success Screen
else:
    st.markdown("""
    <div class="success-box">
        <div class="success-title">✅ Thank You for Your Feedback!</div>
        <p style="font-size: 1.15rem; color: #2c3e50; margin: 0;">
            We've received your review and truly appreciate you taking the time to share your experience with us. 
            Our team will review your feedback shortly!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Info about admin processing
    st.markdown("""
    <div class="info-box">
        <strong>📋 What happens next?</strong><br>
        • Your feedback is now in our system<br>
        • Our admin team will review and analyze it<br>
        • AI-powered insights will be generated<br>
        • We'll take action based on your input
    </div>
    """, unsafe_allow_html=True)
    
    # Celebration for high ratings
    if st.session_state.get('saved_rating', 3) >= 4:
        st.balloons()
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Submit Another Review", type="primary", use_container_width=True):
            st.session_state.submitted = False
            st.session_state.current_rating = 3
            st.rerun()
    
    with col2:
        if st.button("🏠 Start Over", use_container_width=True):
            st.session_state.submitted = False
            st.session_state.current_rating = 3
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #95a5a6; padding: 2rem 0;'>
    <p style='margin: 0; font-size: 0.95rem;'>🤖 AI-Powered Feedback System</p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.85rem;'>Fynd AI Internship Assessment • 2025</p>
</div>
""", unsafe_allow_html=True)

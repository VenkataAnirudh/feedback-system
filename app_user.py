import streamlit as st
from utils import (
    configure_gemini_api,
    save_review,
    generate_user_response,
    generate_admin_summary,
    generate_recommended_actions,
    get_rating_emoji,
    get_rating_text,
    get_sentiment_color
)

# Page config
st.set_page_config(
    page_title="Customer Feedback Portal",
    page_icon="⭐",
    layout="centered"
)

# Professional CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.main { padding: 2rem 1rem; max-width: 800px; margin: 0 auto; background: #f8f9fa; }

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

.ai-response-box {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    margin: 1.5rem 0;
    border-left: 6px solid #667eea;
    box-shadow: 0 8px 32px rgba(0,0,0,0.08);
}

.ai-response-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: #667eea;
    margin-bottom: 1rem;
}

.ai-response-text {
    font-size: 1.15rem;
    line-height: 1.8;
    color: #2c3e50;
}

.api-config-box {
    background: #fff3cd;
    border: 2px solid #ffc107;
    border-radius: 15px;
    padding: 1.5rem;
    margin: 2rem 0;
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
if 'ai_response' not in st.session_state:
    st.session_state.ai_response = ""
if 'current_rating' not in st.session_state:
    st.session_state.current_rating = 3

# API Key Section - ALWAYS VISIBLE
st.markdown('<div class="api-config-box">', unsafe_allow_html=True)
st.markdown("### 🔑 API Configuration")
api_key = st.text_input(
    "Enter your Gemini API Key",
    type="password",
    help="Get free API key: https://makersuite.google.com/app/apikey",
    placeholder="AIzaSy..."
)

if api_key:
    st.success("✅ API Key configured successfully!")
else:
    st.warning("⚠️ Please enter your Gemini API key to enable AI responses")
    st.info("📝 Get your free key at: https://makersuite.google.com/app/apikey")

st.markdown('</div>', unsafe_allow_html=True)

# Main Form
if not st.session_state.submitted:
    with st.form("feedback_form"):
        
        st.markdown("### 📊 Rate Your Experience")
        
        rating = st.slider(
            "Select your rating",
            min_value=1,
            max_value=5,
            value=st.session_state.current_rating,
            help="1 = Poor, 5 = Excellent"
        )
        
        st.session_state.current_rating = rating
        
        # Dynamic rating display
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
            st.caption(f"✅ {char_count} characters - ready to submit!")
        
        # Submit button
        submitted = st.form_submit_button("🚀 Submit Your Feedback")
        
        if submitted:
            if not api_key:
                st.error("❌ Please enter your Gemini API key above!")
            elif char_count < 10:
                st.error("❌ Please write at least 10 characters in your review.")
            else:
                with st.spinner("🤖 Processing your feedback with AI..."):
                    try:
                        # Configure AI
                        model = configure_gemini_api(api_key)
                        
                        if model is None:
                            st.error("❌ Failed to connect to Gemini API. Please check your API key.")
                        else:
                            # Generate AI responses
                            st.info("Generating personalized response...")
                            user_response = generate_user_response(model, rating, review)
                            
                            st.info("Creating summary...")
                            admin_summary = generate_admin_summary(model, rating, review)
                            
                            st.info("Preparing recommendations...")
                            recommended_actions = generate_recommended_actions(model, rating, review)
                            
                            # Save to database
                            st.info("Saving to database...")
                            success = save_review(
                                rating=rating,
                                review=review,
                                ai_response=user_response,
                                ai_summary=admin_summary,
                                recommended_actions=recommended_actions
                            )
                            
                            if success:
                                st.session_state.submitted = True
                                st.session_state.ai_response = user_response
                                st.session_state.saved_rating = rating
                                st.success("✅ Saved successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to save review. Please try again.")
                                
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("💡 Please verify your API key and try again.")

# Success Screen
else:
    st.markdown("""
    <div class="success-box">
        <div class="success-title">✅ Thank You for Your Feedback!</div>
        <p style="font-size: 1.15rem; color: #2c3e50; margin: 0;">
            We've received your review and truly appreciate you taking the time to share your experience with us.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Response
    st.markdown(f"""
    <div class="ai-response-box">
        <div class="ai-response-title">💬 Our Response to You</div>
        <div class="ai-response-text">{st.session_state.ai_response}</div>
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
            st.session_state.ai_response = ""
            st.rerun()
    
    with col2:
        if st.button("🏠 Start Over", use_container_width=True):
            st.session_state.submitted = False
            st.session_state.ai_response = ""
            st.session_state.current_rating = 3
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #95a5a6; padding: 2rem 0;'>
    <p style='margin: 0; font-size: 0.95rem;'>🤖 Powered by Google Gemini AI</p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.85rem;'>Fynd AI Internship Assessment • 2024</p>
</div>
""", unsafe_allow_html=True)

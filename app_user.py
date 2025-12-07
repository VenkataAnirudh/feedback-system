import streamlit as st
from utils import (
    configure_gemini,
    save_review,
    generate_user_response,
    generate_admin_summary,
    generate_recommended_actions,
    get_rating_emoji
)

# Page configuration
st.set_page_config(
    page_title="Leave Your Review",
    page_icon="⭐",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 0.75rem;
        font-size: 1.1rem;
        border-radius: 8px;
        border: none;
        margin-top: 1rem;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .rating-display {
        font-size: 3rem;
        text-align: center;
        margin: 1rem 0;
    }
    .success-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .ai-response {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("⭐ Share Your Experience")
st.markdown(
    "We value your feedback! Please rate your experience and share your thoughts.")

# Initialize session state
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'ai_response' not in st.session_state:
    st.session_state.ai_response = ""

# API Key input (in sidebar for security)
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input(
        "Enter Gemini API Key",
        type="password",
        help="Get your free API key from https://makersuite.google.com/app/apikey"
    )
    st.markdown("---")
    st.markdown("### About")
    st.info("This dashboard collects customer feedback and generates AI-powered responses in real-time.")

    if st.button("🔄 Submit Another Review"):
        st.session_state.submitted = False
        st.session_state.ai_response = ""
        st.rerun()

# Main form
if not st.session_state.submitted:
    with st.form("review_form"):
        st.subheader("📊 How would you rate your experience?")

        # Rating slider with emoji display
        rating = st.slider(
            "Select Rating",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = Poor, 5 = Excellent"
        )

        # Display rating with emoji
        emoji = get_rating_emoji(rating)
        st.markdown(f'<div class="rating-display">{emoji} {rating} Stars</div>',
                    unsafe_allow_html=True)

        st.subheader("✍️ Tell us more about your experience")
        review = st.text_area(
            "Your Review",
            height=150,
            placeholder="Share your thoughts, suggestions, or concerns...",
            help="Please provide detailed feedback to help us improve"
        )

        # Submit button
        submitted = st.form_submit_button("🚀 Submit Review")

        if submitted:
            if not api_key:
                st.error("⚠️ Please enter your Gemini API key in the sidebar.")
            elif not review or len(review.strip()) < 10:
                st.error("⚠️ Please write a review with at least 10 characters.")
            else:
                with st.spinner("🤖 Processing your feedback..."):
                    try:
                        # Configure AI model
                        model = configure_gemini(api_key)

                        # Generate AI responses
                        user_response = generate_user_response(
                            model, rating, review)
                        admin_summary = generate_admin_summary(
                            model, rating, review)
                        recommended_actions = generate_recommended_actions(
                            model, rating, review)

                        # Save to database
                        save_review(
                            rating=rating,
                            review=review,
                            ai_response=user_response,
                            ai_summary=admin_summary,
                            recommended_actions=recommended_actions
                        )

                        # Update session state
                        st.session_state.submitted = True
                        st.session_state.ai_response = user_response
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("Please check your API key and try again.")

# Show success message and AI response
else:
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.success("✅ Thank you! Your review has been submitted successfully.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="ai-response">', unsafe_allow_html=True)
    st.markdown("### 💬 Our Response")
    st.write(st.session_state.ai_response)
    st.markdown('</div>', unsafe_allow_html=True)

    st.balloons()

    # Show another review button prominently
    if st.button("📝 Submit Another Review", type="primary", use_container_width=True):
        st.session_state.submitted = False
        st.session_state.ai_response = ""
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>Powered by AI • Your feedback helps us improve</div>",
    unsafe_allow_html=True
)

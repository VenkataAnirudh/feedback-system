import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import (
    load_reviews,
    configure_gemini_api,
    generate_all_ai_content,
    update_review_with_ai,
    get_sentiment_color,
    get_rating_emoji,
    get_rating_text,
    init_session_storage
)
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Admin Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize storage
init_session_storage()

# Professional CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.main { padding: 1.5rem; background: #f5f7fa; }

.dashboard-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2.5rem;
    border-radius: 20px;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
}

.dashboard-title {
    font-size: 2.8rem;
    font-weight: 700;
    margin: 0;
}

.dashboard-subtitle {
    font-size: 1.15rem;
    opacity: 0.95;
    margin-top: 0.5rem;
}

div[data-testid="stMetricValue"] {
    font-size: 2.2rem;
    font-weight: 700;
}

div[data-testid="metric-container"] {
    background: white;
    padding: 1.8rem;
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border-left: 5px solid #667eea;
}

.review-card {
    background: white;
    padding: 2rem;
    border-radius: 15px;
    margin: 1.5rem 0;
    box-shadow: 0 4px 25px rgba(0,0,0,0.08);
    border-left: 6px solid;
    transition: all 0.3s ease;
}

.review-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 35px rgba(0,0,0,0.15);
}

.rating-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.6rem 1.5rem;
    border-radius: 25px;
    font-weight: 700;
    font-size: 1.1rem;
    color: white;
    box-shadow: 0 3px 10px rgba(0,0,0,0.2);
}

.review-text {
    font-size: 1.1rem;
    line-height: 1.8;
    color: #2c3e50;
    margin: 1.5rem 0;
    padding: 1.5rem;
    background: #f8f9fa;
    border-radius: 12px;
    border-left: 4px solid #667eea;
}

.ai-section {
    background: #e3f2fd;
    padding: 1.5rem;
    border-radius: 12px;
    margin-top: 1rem;
    border-left: 4px solid #2196F3;
}

.ai-section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1976D2;
    margin-bottom: 0.8rem;
}

.ai-section-content {
    font-size: 1.05rem;
    line-height: 1.7;
    color: #424242;
}

.sentiment-card {
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.sentiment-number {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0.5rem 0;
}

.api-config-box {
    background: #fff3cd;
    border: 2px solid #ffc107;
    border-radius: 15px;
    padding: 1.5rem;
    margin-bottom: 2rem;
}

.pending-badge {
    background: #ff9800;
    color: white;
    padding: 0.3rem 0.8rem;
    border-radius: 15px;
    font-size: 0.85rem;
    font-weight: 600;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="dashboard-header">
    <div class="dashboard-title">📊 Admin Analytics Dashboard</div>
    <div class="dashboard-subtitle">AI-powered customer feedback analysis and management</div>
</div>
""", unsafe_allow_html=True)

# API Configuration Section - PROMINENT
st.markdown('<div class="api-config-box">', unsafe_allow_html=True)
st.markdown("### 🔑 AI Configuration (Required)")

col1, col2 = st.columns([3, 1])

with col1:
    api_key = st.text_input(
        "Enter Gemini API Key to generate AI insights",
        type="password",
        help="Get free API key: https://makersuite.google.com/app/apikey",
        placeholder="AIzaSy..."
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if api_key:
        st.success("✅ Configured")
    else:
        st.warning("⚠️ Not Set")

if not api_key:
    st.info("📝 **Get your free API key:** https://makersuite.google.com/app/apikey")
    st.warning("⚠️ AI features (summaries, responses, recommendations) require API key")

st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🎛️ Dashboard Controls")
    st.markdown("---")
    
    if st.button("🔄 Refresh Data", use_container_width=True, type="primary"):
        st.rerun()
    
    st.markdown("---")
    st.markdown("## 📅 Filters")
    
    date_filter = st.selectbox(
        "Time Period",
        ["All Time", "Today", "Last 7 Days", "Last 30 Days"]
    )
    
    rating_filter = st.multiselect(
        "Star Ratings",
        options=[1, 2, 3, 4, 5],
        default=[1, 2, 3, 4, 5],
        format_func=lambda x: f"{get_rating_emoji(x)} {x} Star"
    )
    
    st.markdown("---")
    
    # Show processing button if API key is set
    if api_key:
        st.markdown("## 🤖 AI Processing")
        if st.button("🚀 Process All Pending", use_container_width=True, type="secondary"):
            with st.spinner("Processing reviews with AI..."):
                model = configure_gemini_api(api_key)
                if model:
                    df = load_reviews()
                    processed = 0
                    for idx, row in df.iterrows():
                        if pd.isna(row['ai_response']) or row['ai_response'] == "":
                            ai_content = generate_all_ai_content(model, row['rating'], row['review'])
                            update_review_with_ai(
                                idx,
                                ai_content['ai_response'],
                                ai_content['ai_summary'],
                                ai_content['recommended_actions']
                            )
                            processed += 1
                    st.success(f"✅ Processed {processed} reviews!")
                    st.rerun()
                else:
                    st.error("❌ API configuration failed")

# Load data
df = load_reviews()

# Apply filters
if not df.empty and 'timestamp' in df.columns:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    if date_filter == "Today":
        today = datetime.now().date()
        df = df[df['timestamp'].dt.date == today]
    elif date_filter == "Last 7 Days":
        week_ago = datetime.now() - timedelta(days=7)
        df = df[df['timestamp'] >= week_ago]
    elif date_filter == "Last 30 Days":
        month_ago = datetime.now() - timedelta(days=30)
        df = df[df['timestamp'] >= month_ago]
    
    df = df[df['rating'].isin(rating_filter)]

# Check if data exists
if df.empty:
    st.warning("📭 No reviews found")
    st.info("""
    **To see data:**
    
    1. 🌐 Go to User Dashboard
    2. ⭐ Submit reviews
    3. 🔄 Come back and refresh
    4. 🤖 Click "Process All Pending" to generate AI insights
    """)
    st.stop()

# Count pending reviews
pending_count = len(df[df['ai_response'] == ""])

# Key Metrics
st.markdown("## 📈 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📝 Total Reviews", len(df))

with col2:
    avg_rating = df['rating'].mean()
    st.metric("⭐ Avg Rating", f"{avg_rating:.2f}")

with col3:
    critical = len(df[df['rating'] <= 2])
    st.metric("🚨 Critical", critical)

with col4:
    positive = len(df[df['rating'] >= 4])
    st.metric("✅ Positive", positive)

with col5:
    st.metric("⏳ Pending AI", pending_count, delta=-pending_count if pending_count > 0 else 0, delta_color="inverse")

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Rating Distribution")
    rating_counts = df['rating'].value_counts().sort_index()
    
    colors = [get_sentiment_color(i) for i in rating_counts.index]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"{get_rating_emoji(i)} {i}★" for i in rating_counts.index],
        y=rating_counts.values,
        marker_color=colors,
        text=rating_counts.values,
        textposition='outside',
        textfont=dict(size=14, weight='bold')
    ))
    
    fig.update_layout(
        height=350,
        showlegend=False,
        plot_bgcolor='white',
        margin=dict(t=20, b=20, l=20, r=20),
        yaxis_title="Reviews",
        xaxis_title="Rating"
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 📅 Reviews Timeline")
    if len(df) > 1:
        df['date'] = df['timestamp'].dt.date
        timeline = df.groupby('date').size().reset_index(name='count')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timeline['date'],
            y=timeline['count'],
            mode='lines+markers',
            line=dict(color='#667eea', width=3),
            marker=dict(size=10),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.2)'
        ))
        
        fig.update_layout(
            height=350,
            showlegend=False,
            plot_bgcolor='white',
            margin=dict(t=20, b=20, l=20, r=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 Need more data")

st.markdown("---")

# Sentiment Breakdown
st.markdown("## 🎭 Sentiment Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    negative = len(df[df['rating'] <= 2])
    neg_pct = (negative / len(df) * 100) if len(df) > 0 else 0
    st.markdown(f"""
    <div class="sentiment-card" style="background: #FFEBEE; border-left: 5px solid #D32F2F;">
        <div style="font-size: 3rem;">😞</div>
        <div class="sentiment-number" style="color: #D32F2F;">{negative}</div>
        <div>Negative ({neg_pct:.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    neutral = len(df[df['rating'] == 3])
    neu_pct = (neutral / len(df) * 100) if len(df) > 0 else 0
    st.markdown(f"""
    <div class="sentiment-card" style="background: #FFFDE7; border-left: 5px solid #FBC02D;">
        <div style="font-size: 3rem;">😐</div>
        <div class="sentiment-number" style="color: #FBC02D;">{neutral}</div>
        <div>Neutral ({neu_pct:.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    positive = len(df[df['rating'] >= 4])
    pos_pct = (positive / len(df) * 100) if len(df) > 0 else 0
    st.markdown(f"""
    <div class="sentiment-card" style="background: #E8F5E9; border-left: 5px solid #388E3C;">
        <div style="font-size: 3rem;">😊</div>
        <div class="sentiment-number" style="color: #388E3C;">{positive}</div>
        <div>Positive ({pos_pct:.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Reviews List
st.markdown("## 📝 Customer Reviews with AI Analysis")

# Sorting
col1, col2 = st.columns([3, 1])

with col1:
    sort_by = st.selectbox(
        "Sort by",
        ["Most Recent", "Oldest First", "Highest Rating", "Lowest Rating", "Pending AI First"]
    )

with col2:
    show_critical = st.checkbox("🚨 Critical Only", value=False)

# Apply sorting
if sort_by == "Pending AI First":
    df['has_ai'] = df['ai_response'] != ""
    df = df.sort_values(['has_ai', 'timestamp'], ascending=[True, False])
elif sort_by == "Most Recent":
    df = df.sort_values('timestamp', ascending=False)
elif sort_by == "Oldest First":
    df = df.sort_values('timestamp', ascending=True)
elif sort_by == "Highest Rating":
    df = df.sort_values('rating', ascending=False)
else:  # Lowest Rating
    df = df.sort_values('rating', ascending=True)

if show_critical:
    df = df[df['rating'] <= 2]
    if df.empty:
        st.success("✅ No critical reviews!")
        st.stop()

# Display reviews
for idx, row in df.iterrows():
    rating = int(row['rating'])
    emoji = get_rating_emoji(rating)
    color = get_sentiment_color(rating)
    rating_label = get_rating_text(rating)
    has_ai = row['ai_response'] != ""
    
    st.markdown(
        f'<div class="review-card" style="border-left-color: {color};">',
        unsafe_allow_html=True
    )
    
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(
            f'<span class="rating-badge" style="background: {color};">'
            f'{emoji} {rating} Stars - {rating_label}</span>',
            unsafe_allow_html=True
        )
    with col2:
        if not has_ai:
            st.markdown('<span class="pending-badge">⏳ Pending AI</span>', unsafe_allow_html=True)
    with col3:
        st.caption(f"🕐 {row['timestamp'].strftime('%b %d, %I:%M %p')}")
    
    # Review
    st.markdown(f'<div class="review-text">"{row["review"]}"</div>', unsafe_allow_html=True)
    
    # AI Section or Generate Button
    if has_ai:
        with st.expander("🤖 AI Analysis & Recommendations", expanded=(rating <= 2)):
            st.markdown('<div class="ai-section">', unsafe_allow_html=True)
            st.markdown('<div class="ai-section-title">📋 AI Summary</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ai-section-content">{row["ai_summary"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("")
            
            st.markdown('<div class="ai-section" style="background: #E8F5E9; border-left-color: #388E3C;">', unsafe_allow_html=True)
            st.markdown('<div class="ai-section-title" style="color: #2E7D32;">💬 Customer Response</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ai-section-content">{row["ai_response"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("")
            
            st.markdown('<div class="ai-section" style="background: #FFF3E0; border-left-color: #F57C00;">', unsafe_allow_html=True)
            st.markdown('<div class="ai-section-title" style="color: #E65100;">🎯 Recommended Actions</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ai-section-content">{row["recommended_actions"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        if api_key:
            if st.button(f"🤖 Generate AI Analysis", key=f"gen_{idx}"):
                with st.spinner("Generating AI insights..."):
                    model = configure_gemini_api(api_key)
                    if model:
                        ai_content = generate_all_ai_content(model, row['rating'], row['review'])
                        update_review_with_ai(
                            idx,
                            ai_content['ai_response'],
                            ai_content['ai_summary'],
                            ai_content['recommended_actions']
                        )
                        st.success("✅ AI analysis generated!")
                        st.rerun()
        else:
            st.warning("⚠️ Enter API key above to generate AI insights")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Export
st.markdown("---")
st.markdown("## 💾 Export Data")

col1, col2 = st.columns(2)

with col1:
    csv = df.to_csv(index=False)
    st.download_button(
        "📥 Download CSV",
        csv,
        f"reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "text/csv",
        use_container_width=True
    )

with col2:
    json = df.to_json(orient='records', date_format='iso', indent=2)
    st.download_button(
        "📥 Download JSON",
        json,
        f"reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        "application/json",
        use_container_width=True
    )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #95a5a6; padding: 2rem 0;'>
    <p style='margin: 0; font-size: 0.95rem;'>🤖 Powered by Google Gemini AI</p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.85rem;'>Admin Dashboard • Fynd AI Assessment • 2025</p>
</div>
""", unsafe_allow_html=True)

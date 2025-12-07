import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import (
    load_reviews, configure_gemini_api, generate_all_ai_content,
    update_review_with_ai, get_sentiment_color, get_rating_emoji,
    get_rating_text, time_ago
)
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.main { padding: 1.5rem; background: #f5f7fa; }
.dashboard-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem; border-radius: 20px; color: white; margin-bottom: 2rem;
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
}
.dashboard-title { font-size: 2.5rem; font-weight: 700; margin: 0; }
.dashboard-subtitle { font-size: 1rem; opacity: 0.9; margin-top: 0.5rem; }
div[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; }
div[data-testid="metric-container"] {
    background: white; padding: 1.5rem; border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-left: 5px solid #667eea;
}
.review-card {
    background: white; padding: 1.5rem; border-radius: 15px; margin: 1rem 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-left: 6px solid;
}
.rating-badge {
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.5rem 1.2rem; border-radius: 25px; font-weight: 700;
    font-size: 1rem; color: white; box-shadow: 0 3px 10px rgba(0,0,0,0.2);
}
.review-text {
    font-size: 1.05rem; line-height: 1.7; color: #2c3e50;
    margin: 1rem 0; padding: 1rem; background: #f8f9fa;
    border-radius: 10px; border-left: 4px solid #667eea;
}
.ai-section {
    background: #e3f2fd; padding: 1rem; border-radius: 10px;
    margin: 0.5rem 0; border-left: 4px solid #2196F3;
}
.ai-title { font-size: 0.95rem; font-weight: 700; color: #1976D2; margin-bottom: 0.5rem; }
.ai-content { font-size: 0.95rem; line-height: 1.6; color: #424242; }
.pending-badge {
    background: #ff9800; color: white; padding: 0.3rem 0.8rem;
    border-radius: 15px; font-size: 0.85rem; font-weight: 600;
}
.time-badge {
    background: #e0e0e0; color: #666; padding: 0.3rem 0.8rem;
    border-radius: 15px; font-size: 0.85rem;
}
.new-badge {
    background: #f44336; color: white; padding: 0.3rem 0.8rem;
    border-radius: 15px; font-size: 0.85rem; font-weight: 600;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="dashboard-header">
    <div class="dashboard-title">📊 Admin Analytics Dashboard</div>
    <div class="dashboard-subtitle">Real-time AI-powered customer feedback analysis</div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🤖 AI Processing")
    
    api_key = st.text_input("Gemini API Key", type="password", placeholder="AIzaSy...")
    
    if api_key:
        st.success("✅ API Ready")
        if st.button("🚀 Process All", use_container_width=True, type="primary"):
            model = configure_gemini_api(api_key)
            if model:
                df = load_reviews()
                processed = 0
                progress_bar = st.progress(0)
                status = st.empty()
                
                pending = df[(df['ai_response'] == "") | (df['ai_response'].isna())]
                total = len(pending)
                
                for idx, (df_idx, row) in enumerate(pending.iterrows()):
                    status.text(f"Processing {idx+1}/{total}...")
                    try:
                        ai = generate_all_ai_content(model, row['rating'], row['review'])
                        if update_review_with_ai(df_idx, ai['ai_response'], ai['ai_summary'], ai['recommended_actions']):
                            processed += 1
                    except:
                        pass
                    progress_bar.progress((idx + 1) / total)
                    time.sleep(0.5)
                
                status.empty()
                progress_bar.empty()
                if processed > 0:
                    st.success(f"✅ {processed} processed")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.info("No pending reviews")
            else:
                st.error("❌ API failed")
    else:
        st.warning("⚠️ API required")
    
    st.markdown("---")
    st.markdown("## 📅 Filters")
    
    date_filter = st.selectbox("Time", ["All Time", "Today", "Last 7 Days", "Last 30 Days"])
    rating_filter = st.multiselect("Ratings", [1,2,3,4,5], [1,2,3,4,5], format_func=lambda x: f"{get_rating_emoji(x)} {x}★")
    
    st.markdown("---")
    st.markdown("## ⚙️ Settings")
    
    auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=True)
    
    if st.button("🔃 Refresh Now", use_container_width=True):
        st.rerun()

# Auto-refresh
if auto_refresh:
    time.sleep(30)
    st.rerun()

# Load data
df = load_reviews()

# Apply filters
if not df.empty and 'timestamp' in df.columns:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    if date_filter == "Today":
        df = df[df['timestamp'].dt.date == datetime.now().date()]
    elif date_filter == "Last 7 Days":
        df = df[df['timestamp'] >= datetime.now() - timedelta(days=7)]
    elif date_filter == "Last 30 Days":
        df = df[df['timestamp'] >= datetime.now() - timedelta(days=30)]
    
    df = df[df['rating'].isin(rating_filter)]

# Check data
if df.empty:
    st.warning("📭 No reviews found")
    st.info("Submit reviews via User Dashboard")
    st.stop()

# Count pending
pending_count = len(df[(df['ai_response'] == "") | (df['ai_response'].isna())])

# Metrics
st.markdown("## 📈 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📝 Total", len(df))
with col2:
    st.metric("⭐ Avg", f"{df['rating'].mean():.2f}")
with col3:
    st.metric("🚨 Critical", len(df[df['rating'] <= 2]))
with col4:
    st.metric("✅ Positive", len(df[df['rating'] >= 4]))
with col5:
    st.metric("⏳ Pending", pending_count, delta=-pending_count if pending_count > 0 else 0, delta_color="inverse")

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
        textposition='outside'
    ))
    fig.update_layout(height=300, showlegend=False, plot_bgcolor='white', margin=dict(t=20,b=20,l=20,r=20))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 📅 Timeline")
    if len(df) > 1:
        df['date'] = df['timestamp'].dt.date
        timeline = df.groupby('date').size().reset_index(name='count')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timeline['date'], y=timeline['count'],
            mode='lines+markers', line=dict(color='#667eea', width=3),
            marker=dict(size=10), fill='tozeroy', fillcolor='rgba(102, 126, 234, 0.2)'
        ))
        fig.update_layout(height=300, showlegend=False, plot_bgcolor='white', margin=dict(t=20,b=20,l=20,r=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need more data")

st.markdown("---")

# Reviews
st.markdown("## 📝 Reviews")

col1, col2 = st.columns([3, 1])
with col1:
    sort = st.selectbox("Sort", ["Most Recent", "Oldest", "Highest", "Lowest", "Pending First"])
with col2:
    show_critical = st.checkbox("🚨 Critical Only")

# Sort
if sort == "Pending First":
    df['has_ai'] = ~((df['ai_response'] == "") | (df['ai_response'].isna()))
    df = df.sort_values(['has_ai', 'timestamp'], ascending=[True, False])
elif sort == "Most Recent":
    df = df.sort_values('timestamp', ascending=False)
elif sort == "Oldest":
    df = df.sort_values('timestamp', ascending=True)
elif sort == "Highest":
    df = df.sort_values('rating', ascending=False)
else:
    df = df.sort_values('rating', ascending=True)

if show_critical:
    df = df[df['rating'] <= 2]
    if df.empty:
        st.success("✅ No critical reviews")
        st.stop()

# Display
for idx, row in df.iterrows():
    rating = int(row['rating'])
    emoji = get_rating_emoji(rating)
    color = get_sentiment_color(rating)
    label = get_rating_text(rating)
    has_ai = not ((row['ai_response'] == "") or pd.isna(row['ai_response']))
    
    # Check if new (within 5 minutes)
    time_diff = (datetime.now() - pd.to_datetime(row['timestamp'])).total_seconds()
    is_new = time_diff < 300
    
    st.markdown(f'<div class="review-card" style="border-left-color: {color};">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f'<span class="rating-badge" style="background: {color};">{emoji} {rating}★ - {label}</span>', unsafe_allow_html=True)
    with col2:
        if is_new:
            st.markdown('<span class="new-badge">🆕 NEW</span>', unsafe_allow_html=True)
        elif not has_ai:
            st.markdown('<span class="pending-badge">⏳ Pending</span>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<span class="time-badge">🕐 {time_ago(row["timestamp"])}</span>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="review-text">"{row["review"]}"</div>', unsafe_allow_html=True)
    
    if has_ai:
        with st.expander("🤖 AI Analysis", expanded=(rating <= 2)):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="ai-section">', unsafe_allow_html=True)
                st.markdown('<div class="ai-title">📋 Summary</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="ai-content">{row["ai_summary"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="ai-section" style="background: #E8F5E9; border-left-color: #388E3C;">', unsafe_allow_html=True)
                st.markdown('<div class="ai-title" style="color: #2E7D32;">💬 Response</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="ai-content">{row["ai_response"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="ai-section" style="background: #FFF3E0; border-left-color: #F57C00;">', unsafe_allow_html=True)
            st.markdown('<div class="ai-title" style="color: #E65100;">🎯 Actions</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ai-content">{row["recommended_actions"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        if api_key:
            if st.button(f"Generate AI", key=f"gen_{idx}", type="secondary"):
                model = configure_gemini_api(api_key)
                if model:
                    with st.spinner("Processing..."):
                        ai = generate_all_ai_content(model, row['rating'], row['review'])
                        if update_review_with_ai(idx, ai['ai_response'], ai['ai_summary'], ai['recommended_actions']):
                            st.success("✅ Done")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("❌ Failed")
        else:
            st.warning("⚠️ API key required")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Export
st.markdown("---")
st.markdown("## 💾 Export")
col1, col2 = st.columns(2)
with col1:
    csv = df.to_csv(index=False)
    st.download_button("📥 CSV", csv, f"reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True)
with col2:
    json = df.to_json(orient='records', date_format='iso', indent=2)
    st.download_button("📥 JSON", json, f"reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "application/json", use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #95a5a6; padding: 2rem 0;'>
    <p style='margin: 0;'>🤖 Powered by Google Gemini AI & Google Sheets</p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.85rem;'>Admin Dashboard • Fynd AI • 2025</p>
</div>
""", unsafe_allow_html=True)

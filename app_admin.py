import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import time
from datetime import datetime, timedelta
from utils import (
    load_reviews, configure_gemini_api, 
    update_review_with_ai, get_sentiment_color, get_rating_emoji,
    get_rating_text, time_ago, safe_get_value
)

def generate_tech_analysis(model, rating, review_text):
    """
    Generates tech-focused, concise recommended actions.
    """
    prompt = f"""
    You are a Technical QA System. Analyze this feedback (Rating: {rating}/5):
    "{review_text}"

    1. Write a polite, short response to the user.
    2. Provide 3 General-Purpose TECHNICAL Recommended Actions.
       - Focus on: Code optimization, System quality, Performance, or Tech debt.
       - CONSTRAINT: Each action must be under 10 words.
       - Format: Action 1 | Action 2 | Action 3

    Return strictly valid JSON:
    {{
        "ai_response": "Your response here...",
        "recommended_actions": "Action 1 | Action 2 | Action 3"
    }}
    """
    try:
        response = model.generate_content(prompt)
        text_response = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text_response)
        
        return {
            "ai_response": data.get("ai_response", ""),
            "ai_summary": "See Recommendations", 
            "recommended_actions": data.get("recommended_actions", "")
        }
    except Exception as e:
        return {
            "ai_response": "Error generating analysis.",
            "ai_summary": "Error",
            "recommended_actions": "Manual review required."
        }

st.set_page_config(
    page_title="Admin Dashboard - Fynd AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }
.main { padding: 1.5rem; background: #f5f7fa; }
.dashboard-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2.5rem; border-radius: 20px; color: white; margin-bottom: 2rem;
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
}
.dashboard-title { font-size: 2.8rem; font-weight: 700; margin: 0; text-align: center; }
.dashboard-subtitle { font-size: 1.1rem; opacity: 0.95; margin-top: 0.5rem; text-align: center; }
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
    background: #e3f2fd; padding: 1.2rem; border-radius: 10px;
    margin: 0.8rem 0; border-left: 4px solid #2196F3;
}
.ai-title { font-size: 1rem; font-weight: 700; color: #1976D2; margin-bottom: 0.5rem; }
.ai-content { font-size: 0.95rem; line-height: 1.6; color: #424242; }
.pending-badge {
    background: #ff9800; color: white; padding: 0.3rem 0.8rem;
    border-radius: 15px; font-size: 0.85rem; font-weight: 600;
}
.processed-badge {
    background: #4caf50; color: white; padding: 0.3rem 0.8rem;
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
.api-warning {
    background: #fff3cd; border-left: 4px solid #ffc107;
    padding: 1rem; border-radius: 8px; color: #856404; margin: 1rem 0;
}
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="dashboard-header">
    <div class="dashboard-title">📊 Admin Analytics Dashboard</div>
    <div class="dashboard-subtitle">Real-time AI-powered customer feedback analysis • Fynd AI Assessment</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🤖 AI Processing")
    
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Enter your Gemini API key...",
        help="Get your API key from https://makersuite.google.com/app/apikey"
    )
    
    if api_key:
        st.success("✅ API Key Connected")
        
        if st.button("🚀 Process All Pending", use_container_width=True, type="primary"):
            with st.spinner("Processing reviews..."):
                model = configure_gemini_api(api_key)
                
                if model:
                    df = load_reviews()
                    
                    if df.empty:
                        st.warning("No reviews to process")
                    else:
                        pending_mask = df['ai_response'].apply(lambda x: str(x).strip() == '')
                        pending_df = df[pending_mask]
                        
                        if len(pending_df) == 0:
                            st.info("✅ All reviews already processed!")
                        else:
                            processed_count = 0
                            failed_count = 0
                            
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            for idx, (original_idx, row) in enumerate(pending_df.iterrows()):
                                status_text.text(f"Processing review {idx + 1} of {len(pending_df)}...")
                                
                                try:
                                    ai_content = generate_tech_analysis(
                                        model,
                                        int(row['rating']),
                                        str(row['review'])
                                    )
                                    
                                    success = update_review_with_ai(
                                        original_idx,
                                        ai_content['ai_response'],
                                        ai_content['ai_summary'],
                                        ai_content['recommended_actions']
                                    )
                                    
                                    if success:
                                        processed_count += 1
                                    else:
                                        failed_count += 1
                                    
                                    time.sleep(0.5)
                                    
                                except Exception as e:
                                    failed_count += 1
                                
                                progress_bar.progress((idx + 1) / len(pending_df))
                            
                            status_text.empty()
                            progress_bar.empty()
                            
                            if processed_count > 0:
                                st.success(f"✅ Successfully processed {processed_count} reviews!")
                                if failed_count > 0:
                                    st.warning(f"⚠️ Failed to process {failed_count} reviews")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Failed to process reviews")
                else:
                    st.error("❌ Failed to configure Gemini API")
    else:
        st.info("💡 Enter your Gemini API key to enable AI processing")
    
    st.markdown("---")
    st.markdown("## 📅 Filters")
    
    date_filter = st.selectbox(
        "Time Period",
        ["All Time", "Today", "Last 7 Days", "Last 30 Days"],
        index=0
    )
    
    rating_filter = st.multiselect(
        "Rating Filter",
        options=[1, 2, 3, 4, 5],
        default=[1, 2, 3, 4, 5],
        format_func=lambda x: f"{get_rating_emoji(x)} {x} Star{'s' if x > 1 else ''}"
    )
    
    st.markdown("---")
    st.markdown("## ⚙️ Settings")
    
    auto_refresh = st.checkbox(
        "🔄 Auto-refresh (30s)",
        value=False,
        help="Automatically refresh dashboard every 30 seconds"
    )
    
    if st.button("🔃 Refresh Now", use_container_width=True):
        st.rerun()

df = load_reviews()

if not df.empty and 'timestamp' in df.columns:
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])
    
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

if df.empty:
    st.warning("📭 No reviews found matching your filters")
    st.info("💡 Try adjusting your filters or submit reviews via the User Dashboard")
    st.stop()

total_reviews = len(df)
avg_rating = df['rating'].mean()
critical_reviews = len(df[df['rating'] <= 2])
positive_reviews = len(df[df['rating'] >= 4])
pending_count = len(df[df['ai_response'].apply(lambda x: str(x).strip() == '')])

st.markdown("## 📈 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📝 Total Reviews", total_reviews)
with col2:
    st.metric("⭐ Average Rating", f"{avg_rating:.2f}")
with col3:
    st.metric("🚨 Critical (≤2★)", critical_reviews)
with col4:
    st.metric("✅ Positive (≥4★)", positive_reviews)
with col5:
    st.metric("⏳ Pending AI", pending_count, delta=f"-{pending_count}" if pending_count > 0 else "All done", delta_color="inverse")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Rating Distribution")
    try:
        rating_counts = df['rating'].value_counts().sort_index()
        colors = [get_sentiment_color(int(i)) for i in rating_counts.index]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[f"{get_rating_emoji(int(i))} {int(i)}★" for i in rating_counts.index],
            y=rating_counts.values,
            marker_color=colors,
            text=rating_counts.values,
            textposition='outside',
            textfont=dict(size=14)
        ))
        fig.update_layout(
            height=320, showlegend=False, plot_bgcolor='white',
            margin=dict(t=20, b=20, l=20, r=20),
            xaxis_title="Rating", yaxis_title="Count"
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info("📊 Chart unavailable")

with col2:
    st.markdown("### 📅 Reviews Timeline")
    try:
        if len(df) > 1:
            df_timeline = df.copy()
            df_timeline['date'] = df_timeline['timestamp'].dt.date
            timeline = df_timeline.groupby('date').size().reset_index(name='count')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=timeline['date'], y=timeline['count'],
                mode='lines+markers', line=dict(color='#667eea', width=3),
                marker=dict(size=10, color='#667eea'),
                fill='tozeroy', fillcolor='rgba(102, 126, 234, 0.2)'
            ))
            fig.update_layout(
                height=320, showlegend=False, plot_bgcolor='white',
                margin=dict(t=20, b=20, l=20, r=20),
                xaxis_title="Date", yaxis_title="Reviews"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Need more data points")
    except Exception as e:
        st.info("📊 Timeline unavailable")

st.markdown("---")

st.markdown("## 📝 Customer Reviews")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    sort_option = st.selectbox(
        "Sort by",
        ["Most Recent", "Oldest", "Highest Rated", "Lowest Rated", "Pending First"],
        index=0
    )

with col2:
    show_critical = st.checkbox("🚨 Critical Only (≤2★)")

with col3:
    display_mode = st.selectbox("Display", ["Show All", "Recent 5", "Recent 10"], index=0)

try:
    if sort_option == "Pending First":
        df['has_ai'] = df['ai_response'].apply(lambda x: str(x).strip() != '')
        df = df.sort_values(['has_ai', 'timestamp'], ascending=[True, False])
    elif sort_option == "Most Recent":
        df = df.sort_values('timestamp', ascending=False)
    elif sort_option == "Oldest":
        df = df.sort_values('timestamp', ascending=True)
    elif sort_option == "Highest Rated":
        df = df.sort_values(['rating', 'timestamp'], ascending=[False, False])
    else:
        df = df.sort_values(['rating', 'timestamp'], ascending=[True, False])
except Exception as e:
    pass

if show_critical:
    df = df[df['rating'] <= 2]
    if df.empty:
        st.success("✅ No critical reviews found!")
        st.stop()

if display_mode == "Recent 5":
    df = df.head(5)
    st.info(f"📊 Showing 5 most recent reviews")
elif display_mode == "Recent 10":
    df = df.head(10)
    st.info(f"📊 Showing 10 most recent reviews")
else:
    st.info(f"📊 Showing all {len(df)} reviews")

for idx, row in df.iterrows():
    try:
        rating = int(row.get('rating', 3))
        review_text = safe_get_value(row, 'review', 'No review text')
        timestamp = row.get('timestamp', datetime.now())
        
        ai_actions = safe_get_value(row, 'recommendation_actions') 
        if not ai_actions:
            ai_actions = safe_get_value(row, 'recommended_actions')
            
        ai_response = safe_get_value(row, 'ai_response')
        
        emoji = get_rating_emoji(rating)
        color = get_sentiment_color(rating)
        label = get_rating_text(rating)
        has_ai = len(ai_response) > 0
        
        try:
            time_diff = (datetime.now() - pd.to_datetime(timestamp)).total_seconds()
            is_new = time_diff < 300
        except:
            is_new = False
        
        st.markdown(f'<div class="review-card" style="border-left-color: {color};">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f'<span class="rating-badge" style="background: {color};">{emoji} {rating}★ - {label}</span>', unsafe_allow_html=True)
        
        with col2:
            if is_new:
                st.markdown('<span class="new-badge">🆕 NEW</span>', unsafe_allow_html=True)
            elif has_ai:
                st.markdown('<span class="processed-badge">✅ AI Processed</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="pending-badge">⏳ Pending AI</span>', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f'<span class="time-badge">🕐 {time_ago(timestamp)}</span>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="review-text">"{review_text}"</div>', unsafe_allow_html=True)
        
        if has_ai:
            if ai_actions:
                st.markdown(f'''
                <div class="ai-section">
                    <div class="ai-title">🎯 Recommended Actions</div>
                    <div class="ai-content">{ai_actions}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            if ai_response:
                with st.expander("💬 View Customer Response"):
                    st.markdown('<div class="ai-section" style="background: #E8F5E9; border-left-color: #388E3C;"><div class="ai-content">' + ai_response + '</div></div>', unsafe_allow_html=True)
        else:
            if not api_key:
                st.markdown('<div class="api-warning"><strong>🔑 API Key Required</strong><br>Please enter your Gemini API key in the sidebar to generate AI analysis.</div>', unsafe_allow_html=True)
            else:
                if st.button(f"🤖 Generate AI Analysis", key=f"gen_{idx}", type="secondary"):
                    model = configure_gemini_api(api_key)
                    if model:
                        with st.spinner("Generating..."):
                            try:
                                ai_content = generate_tech_analysis(model, rating, review_text)
                                success = update_review_with_ai(idx, ai_content['ai_response'], ai_content['ai_summary'], ai_content['recommended_actions'])
                                
                                if success:
                                    st.success("✅ AI analysis generated!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.warning("⚠️ Update failed")
                            except Exception as e:
                                st.warning(f"⚠️ Generation failed")
                    else:
                        st.warning("⚠️ API connection failed")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    except Exception as e:
        continue

st.markdown("---")
st.markdown("## 💾 Export Data")

col1, col2, col3 = st.columns(3)

with col1:
    csv_data = df.to_csv(index=False)
    st.download_button("📥 Download CSV", csv_data, f"reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True)

with col2:
    json_data = df.to_json(orient='records', date_format='iso', indent=2)
    st.download_button("📥 Download JSON", json_data, f"reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "application/json", use_container_width=True)

with col3:
    pending_df = df[df['ai_response'].apply(lambda x: str(x).strip() == '')]
    if not pending_df.empty:
        pending_csv = pending_df.to_csv(index=False)
        st.download_button("📥 Pending Reviews", pending_csv, f"pending_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True)

st.markdown("---")
st.markdown('<div style="text-align: center; color: #95a5a6; padding: 2rem 0;"><p style="margin: 0;">🤖 Powered by Google Gemini AI & Google Sheets</p><p style="margin: 0.5rem 0 0 0;">Admin Dashboard • Fynd AI Assessment • 2025</p></div>', unsafe_allow_html=True)

if auto_refresh:
    time.sleep(30)
    st.rerun()

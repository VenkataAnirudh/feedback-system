import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_reviews, get_sentiment_color, get_rating_emoji
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .review-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2196F3;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .critical-review {
        border-left-color: #ff4444 !important;
        background-color: #fff5f5;
    }
    .positive-review {
        border-left-color: #44ff44 !important;
        background-color: #f5fff5;
    }
    .rating-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("📊 Admin Dashboard - Customer Feedback Analytics")
st.markdown("Real-time monitoring and analysis of customer reviews")

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filters")

    # Auto-refresh toggle
    auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=False)

    if st.button("🔃 Refresh Data", use_container_width=True):
        st.rerun()

    st.markdown("---")

    # Date filter
    date_filter = st.selectbox(
        "📅 Time Period",
        ["All Time", "Today", "Last 7 Days", "Last 30 Days"]
    )

    # Rating filter
    rating_filter = st.multiselect(
        "⭐ Filter by Rating",
        options=[1, 2, 3, 4, 5],
        default=[1, 2, 3, 4, 5]
    )

    st.markdown("---")
    st.info("💡 **Tip**: Critical reviews (1-2 stars) are highlighted in red and require immediate attention.")

# Auto-refresh logic
if auto_refresh:
    st.rerun()

# Load data
df = load_reviews()

# Filter data by date
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

    # Filter by rating
    df = df[df['rating'].isin(rating_filter)]

# Check if data exists
if df.empty:
    st.warning("📭 No reviews yet. Waiting for customer feedback...")
    st.info(
        "Reviews submitted through the User Dashboard will appear here in real-time.")
    st.stop()

# Key Metrics Row
st.markdown("### 📈 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_reviews = len(df)
    st.metric("Total Reviews", total_reviews)

with col2:
    avg_rating = df['rating'].mean()
    st.metric("Average Rating", f"{avg_rating:.2f} ⭐")

with col3:
    critical_reviews = len(df[df['rating'] <= 2])
    st.metric("Critical Reviews", critical_reviews,
              delta=None, delta_color="inverse")

with col4:
    positive_reviews = len(df[df['rating'] >= 4])
    st.metric("Positive Reviews", positive_reviews, delta=None)

with col5:
    if len(df) > 1:
        # Calculate trend (recent vs older reviews)
        df_sorted = df.sort_values('timestamp')
        half = len(df_sorted) // 2
        recent_avg = df_sorted.tail(half)['rating'].mean()
        older_avg = df_sorted.head(half)['rating'].mean()
        trend = recent_avg - older_avg
        st.metric("Trend", f"{trend:+.2f}", delta=f"{trend:+.2f}")
    else:
        st.metric("Trend", "N/A")

st.markdown("---")

# Charts Row
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Rating Distribution")
    rating_counts = df['rating'].value_counts().sort_index()

    fig = px.bar(
        x=rating_counts.index,
        y=rating_counts.values,
        labels={'x': 'Rating (Stars)', 'y': 'Number of Reviews'},
        color=rating_counts.values,
        color_continuous_scale=['#ff4444', '#ffaa00',
                                '#ffff44', '#aaff44', '#44ff44']
    )
    fig.update_layout(
        showlegend=False,
        height=300,
        xaxis=dict(tickmode='linear', tick0=1, dtick=1)
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 📅 Reviews Over Time")
    if len(df) > 1:
        # Group by date
        df['date'] = df['timestamp'].dt.date
        timeline = df.groupby('date').size().reset_index(name='count')

        fig = px.line(
            timeline,
            x='date',
            y='count',
            labels={'date': 'Date', 'count': 'Number of Reviews'},
            markers=True
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need more data points to show timeline")

st.markdown("---")

# Reviews List
st.markdown("### 📝 All Reviews")

# Sort options
col1, col2 = st.columns([3, 1])
with col1:
    sort_by = st.selectbox(
        "Sort by",
        ["Most Recent", "Oldest First", "Highest Rating", "Lowest Rating"]
    )
with col2:
    show_critical_only = st.checkbox("🚨 Critical Only", value=False)

# Apply sorting
if sort_by == "Most Recent":
    df = df.sort_values('timestamp', ascending=False)
elif sort_by == "Oldest First":
    df = df.sort_values('timestamp', ascending=True)
elif sort_by == "Highest Rating":
    df = df.sort_values('rating', ascending=False)
elif sort_by == "Lowest Rating":
    df = df.sort_values('rating', ascending=True)

# Filter critical reviews
if show_critical_only:
    df = df[df['rating'] <= 2]
    if df.empty:
        st.success("✅ No critical reviews found!")
        st.stop()

# Display reviews
for idx, row in df.iterrows():
    rating = int(row['rating'])
    emoji = get_rating_emoji(rating)
    color = get_sentiment_color(rating)

    # Determine card class
    card_class = "review-card"
    if rating <= 2:
        card_class += " critical-review"
    elif rating >= 4:
        card_class += " positive-review"

    with st.container():
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)

        # Header with rating and timestamp
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(
                f'<span class="rating-badge" style="background-color: {color}; color: white;">'
                f'{emoji} {rating} Stars</span>',
                unsafe_allow_html=True
            )
        with col2:
            st.caption(row['timestamp'].strftime("%Y-%m-%d %H:%M"))

        # Review content
        st.markdown("**Customer Review:**")
        st.write(row['review'])

        # Expandable sections
        with st.expander("🤖 AI Analysis"):
            st.markdown("**Summary:**")
            st.info(row['ai_summary'])

            st.markdown("**Recommended Actions:**")
            st.warning(row['recommended_actions'])

        with st.expander("💬 AI Response (Sent to Customer)"):
            st.success(row['ai_response'])

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("")

# Export functionality
st.markdown("---")
st.markdown("### 💾 Export Data")
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

with col2:
    json = df.to_json(orient='records', date_format='iso')
    st.download_button(
        label="📥 Download JSON",
        data=json,
        file_name=f"reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>Admin Dashboard • Powered by AI Analytics</div>",
    unsafe_allow_html=True
)

# AI-Powered Feedback System

A two-dashboard web application for collecting and analyzing customer feedback using AI.

## 🌟 Features

### User Dashboard
- ⭐ Star rating system (1-5)
- ✍️ Review submission interface
- 🤖 AI-generated personalized responses
- 📱 Mobile-responsive design

### Admin Dashboard
- 📊 Real-time analytics and metrics
- 📈 Visual charts and trends
- 🔍 Filtering and sorting capabilities
- 💾 Data export (CSV/JSON)
- 🤖 AI-generated summaries and action recommendations

## 🚀 Local Setup

### Prerequisites
- Python 3.8 or higher
- Gemini API key (free at https://makersuite.google.com/app/apikey)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd task2-feedback-system
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create data directory:
```bash
mkdir data
```

5. Run User Dashboard:
```bash
streamlit run app_user.py
```

6. Run Admin Dashboard (in a new terminal):
```bash
streamlit run app_admin.py
```

## 🌐 Deployment on Streamlit Cloud

### Step 1: Prepare Repository
1. Push all files to GitHub
2. Ensure `.streamlit/config.toml` is included
3. Commit `data/` directory (can be empty initially)

### Step 2: Deploy User Dashboard
1. Go to https://share.streamlit.io
2. Click "New app"
3. Select your repository
4. Set main file: `app_user.py`
5. Click "Deploy"

### Step 3: Deploy Admin Dashboard
1. Click "New app" again
2. Select same repository
3. Set main file: `app_admin.py`
4. Click "Deploy"

### Step 4: Configure Secrets (Optional)
If you want to pre-configure API key:
1. Go to app settings
2. Add secret: `GEMINI_API_KEY = "your-key-here"`
3. Update code to use `st.secrets["GEMINI_API_KEY"]`

## 📁 Project Structure

```
task2-feedback-system/
│
├── app_user.py              # User Dashboard
├── app_admin.py             # Admin Dashboard
├── utils.py                 # Shared utilities
├── requirements.txt         # Python dependencies
├── .streamlit/
│   └── config.toml         # Streamlit configuration
├── data/
│   └── reviews.csv         # Data storage
└── README.md               # This file
```

## 🔧 Technology Stack

- **Frontend**: Streamlit
- **AI**: Google Gemini API
- **Data**: Pandas, CSV storage
- **Visualization**: Plotly
- **Deployment**: Streamlit Cloud

## 📊 Data Storage

Reviews are stored in `data/reviews.csv` with the following fields:
- `timestamp`: Submission date/time
- `rating`: Star rating (1-5)
- `review`: Customer review text
- `ai_response`: AI-generated user response
- `ai_summary`: Admin summary
- `recommended_actions`: Suggested next steps

## 🎯 Usage

### For Customers (User Dashboard)
1. Select a star rating
2. Write your review
3. Submit and receive AI-powered response

### For Administrators (Admin Dashboard)
1. View real-time metrics
2. Analyze trends and patterns
3. Review AI recommendations
4. Export data for further analysis

## 🔐 Security Notes

- API keys should be entered securely (password input)
- Never commit API keys to repository
- Use Streamlit secrets for production deployment
- Data is stored locally/on deployment server

## 📝 License

MIT License - Feel free to use for your projects

## 👨‍💻 Author

Created for Fynd AI Internship Take-Home Assessment
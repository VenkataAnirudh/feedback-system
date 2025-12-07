# 📊 AI-Powered Customer Feedback System

A full-stack feedback solution built with **Streamlit**, **Google Sheets**, and **Google Gemini AI**. This system consists of two distinct interfaces: a user-facing portal for submitting reviews and an admin dashboard for real-time analytics and AI-driven insights.

## 🚀 Features

### 👤 User Portal (`app_user.py`) - [![User App](https://img.shields.io/badge/Open-User_App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://feedback-system-hvggjudf6px7eknazwj2zq.streamlit.app/)

  * **Interactive Rating System:** Drag slider for star ratings (1-5) with dynamic emojis and sentiment colors.
  * **Feedback Form:** Text area with character count validation.
  * **Real-time Submission:** Instantly saves data to Google Sheets.
  * **Engagement:** Success animations (balloons) for positive feedback.

### 🛡️ Admin Dashboard (`app_admin.py`) - [![Admin Dashboard](https://img.shields.io/badge/Open-Admin_Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://feedback-system-ceyvk7ryjljkehbfge5a2t.streamlit.app/)

  * **Live Analytics:** Key metrics (Total Reviews, Average Rating, Critical Issues).
  * **Data Visualization:** Interactive charts for rating distribution and review volume over time using Plotly.
  * **AI Intelligence (Gemini 2.5 Flash):**
      * **Auto-Analysis:** Generates polite customer responses.
      * **Tech Recommendations:** Provides specific, actionable 10-word technical recommended actions for dev teams.
  * **Filtering & Sorting:** Filter by date range, star rating, or processing status.
  * **Export Data:** Download reports in CSV or JSON formats.

## 🛠️ Tech Stack

  * **Frontend:** [Streamlit](https://streamlit.io/)
  * **Database:** Google Sheets (via `gspread`)
  * **AI Engine:** Google Gemini API (`google-generativeai`)
  * **Visualization:** Plotly Express / Graph Objects
  * **Language:** Python 3.11+

## 📂 Project Structure

```bash
feedback-system/
├── app_user.py       # Customer-facing feedback submission app
├── app_admin.py      # Admin dashboard for analytics & AI
├── utils.py          # Shared logic (Google Sheets, Gemini AI, Data processing)
├── requirements.txt  # Python dependencies
└── README.md         # Project documentation
```

## ⚙️ Setup & Installation

### 1\. Clone the Repository

```bash
git clone https://github.com/your-username/feedback-system.git
cd feedback-system
```

### 2\. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3\. Configure Secrets

Create a `.streamlit/secrets.toml` file in your project root to handle sensitive keys.

**Required Structure:**

```toml
SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n..."
client_email = "your-service-account-email"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

*\> **Note:** You can download the JSON key from your Google Cloud Console and copy the values into this format.*

## 🏃‍♂️ How to Run

### Run the User App

```bash
streamlit run app_user.py
```

### Run the Admin Dashboard

```bash
streamlit run app_admin.py
```

*\> The admin app requires a Gemini API Key, which you can enter directly in the sidebar.*

## 🤖 AI Features Explained

The system uses **Gemini 2.5 Flash Lite** to process reviews. When the admin clicks **"Process All Pending"**, the system:

1.  **Analyzes Sentiment:** Determines the tone of the review.
2.  **Drafts a Response:** Creates a warm, professional reply for the customer.
3.  **Generates Recommended Actions:** Creates 3 strictly technical, actionable steps (max 10 words each) for the engineering/QA team to address the feedback.

## 📄 License

This project is open-source and available under the MIT License.


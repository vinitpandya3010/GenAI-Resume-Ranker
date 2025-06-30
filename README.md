🤖 GenAI Resume Ranker
A Streamlit web application that leverages Azure OpenAI and LangChain to intelligently rank resumes against a given job description. This tool helps HR professionals and hiring managers quickly identify the most qualified candidates from a pool of applicants.
✨ Features
Job Description Input: Paste any job description into a simple text area.
Bulk Resume Upload: Upload up to 10 resume PDFs simultaneously.
AI-Powered Analysis: Uses Azure OpenAI via LangChain to compare each resume against the job description.
Scoring & Ranking: Each resume is assigned a percentage score based on its relevance.
Detailed Breakdown: For each candidate, view a summary, key strengths, and potential weaknesses.
Secure Credential Handling: API keys and endpoints are loaded from a .env file, not hard-coded in the app.
User-Friendly Interface: Clean and intuitive UI built with Streamlit.
📸 Screenshot
(It's highly recommended to take a screenshot of your running application and save it as screenshot.png in the project directory for a more professional look.)
![alt text](screenshot.png)
🛠️ Tech Stack
Framework: Streamlit
LLM Orchestration: LangChain
AI Model: Azure Chat OpenAI
PDF Processing: PyPDF
Configuration: Python-dotenv
🚀 Getting Started
Follow these instructions to get a copy of the project up and running on your local machine.
Prerequisites
Python 3.8+
An active Azure account with access to the Azure OpenAI service. You will need:
Your Azure OpenAI resource Endpoint.
An API Key.
The Deployment Name of your model (e.g., gpt-4o or gpt-35-turbo).


git clone https://github.com/your-username/resume-ranker.git
cd resume-ranker

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate


pip install -r requirements.txt


# Azure OpenAI Credentials
AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com/"
AZURE_OPENAI_API_KEY="your_actual_api_key_here"
AZURE_OPENAI_API_VERSION="2024-02-01"
AZURE_OPENAI_DEPLOYMENT_NAME="your_deployment_name"


# .gitignore
.env
venv/
__pycache__/


streamlit run app.py


/
├── .env                # Stores secret credentials (you must create this)
├── app.py              # The main Streamlit application code
├── requirements.txt    # Python package dependencies
└── README.md           # This file



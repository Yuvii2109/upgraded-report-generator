# EDXSO Survey Report Generator

A Streamlit application designed to automate the analysis and reporting of Student Well-Being Surveys. This tool processes Excel/CSV data, generates AI-powered qualitative insights using **Google Gemini**, and outputs high-fidelity reports in **HTML** and **PDF** formats.

## Key Features

- **Batch Processing:** Select and process multiple schools from a single dataset simultaneously.
- **AI Integration:** Uses Google Gemini (Pro/Flash) to generate Executive Summaries, Key Findings, and Strategic Recommendations.
- **Automated Scoring:** Calculates student stress levels (Balanced to Severe) based on Likert scale responses.
- **PDF Generation:** Utilizes **Playwright** (Headless Chromium) to render pixel-perfect, single-page PDF reports.
- **Secure:** Built-in rate limiting and safe-mode for API stability.

## Tech Stack

- **Frontend:** Streamlit
- **Data Processing:** Pandas, OpenPyXL
- **AI Model:** Google Generative AI (Gemini)
- **PDF Engine:** Playwright

## Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Yuvii2109/upgraded-report-generator.git
   cd edxso-report-generator
   
2. **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    
3. **Install Playwright Browsers:** Required for PDF generation functionality.
    ```bash
    playwright install chromium
    
4. **Run the application:**
    ```bash
    streamlit run app.py

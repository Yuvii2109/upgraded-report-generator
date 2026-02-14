import streamlit as st
import pandas as pd
import io
import zipfile
import google.generativeai as genai
import time
import subprocess
import sys
import os
import tempfile

# --- CONFIGURATION ---
st.set_page_config(page_title="EDXSO Survey Report Generator", layout="wide")

# --- HTML TEMPLATE (ORIGINAL GOLD STANDARD) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Well-Being Survey Report - [SCHOOL_NAME]</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f9fafb; color: #1e293b; -webkit-print-color-adjust: exact; }
        .report-section { background: #ffffff; margin-bottom: 3rem; overflow: hidden; border: 1px solid #f1f5f9; border-radius: 1.5rem; }
        .text-navy { color: #0c4a6e; }
        .hero-gradient { background: linear-gradient(135deg, #0c4a6e 0%, #075985 100%); }
        .chart-bar-bg { background-color: #f1f5f9; border-radius: 9999px; height: 1.5rem; width: 100%; overflow: hidden; position: relative; }
        .chart-bar-fill { height: 100%; border-radius: 9999px; }
        .legend-dot { width: 12px; height: 12px; border-radius: 3px; display: inline-block; margin-right: 6px; }
    </style>
</head>
<body class="p-8">
    <div class="max-w-5xl mx-auto">
        <header class="report-section hero-gradient text-white p-12 flex flex-col items-center text-center border-none">
            <div class="mb-10 bg-white p-4 rounded-xl">
                <img src="https://i.ibb.co/jP5j8vf8/Screenshot-2026-01-30-at-5-16-07-PM.png" alt="EDXSO Logo" class="h-20 w-auto">
            </div>
            <p class="uppercase tracking-widest text-blue-200 font-semibold mb-2">[SCHOOL_NAME]</p>
            <h1 class="text-5xl font-extrabold mb-6 leading-tight">Student Well-Being & <br>Assessment Experience Survey</h1>
            <div class="w-24 h-1 bg-blue-400 mb-8"></div>
            <div class="space-y-2 text-blue-100">
                <p class="text-xl font-medium">SURVEY REPORT</p>
                <p>Established [EST_YEAR]</p>
                <p class="opacity-80">www.edxso.com</p>
            </div>
        </header>

        <section id="executive-summary" class="report-section">
            <div class="p-10 md:p-12">
                <div class="flex items-center gap-3 mb-8 border-b border-gray-50 pb-6">
                    <span class="p-2 bg-blue-50 rounded-lg">
                        <svg class="w-6 h-6 text-blue-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    </span>
                    <h2 class="text-3xl font-bold text-navy uppercase tracking-tight">Executive Summary</h2>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-12 mb-10">
                    <div class="space-y-4 text-gray-700 leading-relaxed text-lg">
                        <p>[EXEC_SUMMARY_P1]</p>
                        <p>[EXEC_SUMMARY_P2]</p>
                    </div>
                    <div class="space-y-4 text-gray-700 leading-relaxed text-lg">
                        <p class="font-semibold text-navy">[EXEC_SUMMARY_KEY_FINDING]</p>
                        <p>[EXEC_SUMMARY_CONCLUSION]</p>
                    </div>
                </div>
                <div class="p-8 border-l-4 border-blue-600 mb-12 italic text-gray-600 bg-slate-50/50 text-xl rounded-r-xl">
                    "[INSERT_KEY_QUOTE]"
                </div>
            </div>
        </section>

        <section id="overview" class="report-section p-10 md:p-12">
            <div class="flex flex-col md:flex-row gap-12">
                <div class="md:w-1/3">
                    <img src="https://i.ibb.co/VYdmHbWy/Screenshot-2026-01-30-at-5-19-42-PM.png" alt="Overview Icon" class="rounded-xl mb-6 w-full object-cover">
                    <h2 class="text-2xl font-bold text-navy mb-4 uppercase">Survey Overview</h2>
                    <p class="text-gray-600 leading-relaxed">Structured snapshot outlining scale, mode, and analytical logic used to capture student perspectives.</p>
                </div>
                <div class="md:w-2/3 space-y-2">
                    <div class="flex items-center p-5 border-b border-gray-100">
                        <div class="w-40 font-bold text-navy uppercase text-xs tracking-wider">Survey Name:</div>
                        <div class="text-gray-700">Student Well-Being & Assessment Experience Survey</div>
                    </div>
                    <div class="flex items-center p-5 border-b border-gray-100">
                        <div class="w-40 font-bold text-navy uppercase text-xs tracking-wider">Participants:</div>
                        <div class="text-gray-700">[COUNT] Students</div>
                    </div>
                    <div class="flex items-center p-5 border-b border-gray-100">
                        <div class="w-40 font-bold text-navy uppercase text-xs tracking-wider">Mode:</div>
                        <div class="text-gray-700">[MODE]</div>
                    </div>
                    <div class="flex items-center p-5 border-b border-gray-100">
                        <div class="w-40 font-bold text-navy uppercase text-xs tracking-wider">Nature:</div>
                        <div class="text-gray-700">Anonymous, self-reported</div>
                    </div>
                    <div class="flex items-center p-5 border-b border-gray-100">
                        <div class="w-40 font-bold text-navy uppercase text-xs tracking-wider">Focus:</div>
                        <div class="text-gray-700">Emotional impact of assessments</div>
                    </div>
                </div>
            </div>
        </section>

        <section class="grid grid-cols-1 md:grid-cols-2 gap-12 mb-16">
            <div class="p-10 border border-slate-100 rounded-2xl bg-white">
                <h2 class="text-2xl font-bold text-navy mb-8 uppercase tracking-widest flex items-center gap-2">Objectives</h2>
                <ul class="space-y-6">
                    <li class="flex gap-4"><span class="text-blue-600 font-bold text-xl">01</span><p class="text-gray-700">Collect evidence on emotional responses to tests.</p></li>
                    <li class="flex gap-4"><span class="text-blue-600 font-bold text-xl">02</span><p class="text-gray-700">Analyze stress associated with performance expectations.</p></li>
                    <li class="flex gap-4"><span class="text-blue-600 font-bold text-xl">03</span><p class="text-gray-700">Classify students into defined stress categories.</p></li>
                </ul>
            </div>
            <div class="p-0">
                <img src="https://i.ibb.co/kV9wrJ8q/Screenshot-2026-01-30-at-5-20-37-PM.png" alt="Methodology" class="rounded-2xl mb-6 w-full">
                <h2 class="text-2xl font-bold text-navy mb-4 uppercase">Design & Methodology</h2>
                <p class="text-gray-600 mb-6">20 structured statements on a 5-point scale from <span class="font-semibold">Never</span> to <span class="font-semibold">Always</span>.</p>
            </div>
        </section>

        <section id="scoring" class="report-section p-10 md:p-12">
            <div class="mb-12">
                <h2 class="text-4xl font-extrabold text-navy tracking-tight mb-2 uppercase">Scoring Framework</h2>
                <div class="h-1 w-20 bg-blue-600"></div>
            </div>
            <div class="space-y-1">
                 [INSERT_FULL_SCORING_TABLE_FROM_USER_PROMPT]
            </div>
            <div class="mt-12 p-6 bg-slate-50 rounded-xl text-gray-500 text-sm">
                <p>Note: Participation was anonymous. Scoring logic was applied strictly without subjective interpretation.</p>
            </div>
        </section>

        <section id="results" class="report-section p-10 md:p-12">
            <div class="mb-12 text-center">
                <h2 class="text-3xl font-bold text-navy mb-2 uppercase tracking-tighter">Student Well-Being</h2>
                <p class="text-xl text-gray-400">Stress Category Distribution</p>
            </div>
            <div class="mb-16 flex justify-center">
                <img src="https://i.ibb.co/bR1yz5p6/Screenshot-2026-01-30-at-5-21-18-PM.png" alt="Stress Distribution Chart" class="w-full max-w-4xl">
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12">
                <div class="pb-6 border-b-2 border-green-500">
                    <div class="flex justify-between items-baseline mb-2">
                        <h3 class="font-bold text-gray-900 uppercase text-sm tracking-widest">Emotionally Balanced</h3>
                        <span class="text-3xl font-black text-green-600">[VAL_BALANCED]</span>
                    </div>
                    <p class="text-sm text-gray-500">[PCT_BALANCED]% — Stable emotional states.</p>
                </div>
                <div class="pb-6 border-b-2 border-blue-500">
                    <div class="flex justify-between items-baseline mb-2">
                        <h3 class="font-bold text-gray-900 uppercase text-sm tracking-widest">Mildly Stressed</h3>
                        <span class="text-3xl font-black text-blue-600">[VAL_MILD]</span>
                    </div>
                    <p class="text-sm text-gray-500">[PCT_MILD]% — Minor stress levels.</p>
                </div>
                <div class="pb-6 border-b-2 border-yellow-500">
                    <div class="flex justify-between items-baseline mb-2">
                        <h3 class="font-bold text-gray-900 uppercase text-sm tracking-widest">Moderately Stressed</h3>
                        <span class="text-3xl font-black text-yellow-600">[VAL_MOD]</span>
                    </div>
                    <p class="text-sm text-gray-500">[PCT_MOD]% — Significant challenges.</p>
                </div>
                <div class="pb-6 border-b-2 border-orange-500">
                    <div class="flex justify-between items-baseline mb-2">
                        <h3 class="font-bold text-gray-900 uppercase text-sm tracking-widest">Highly Stressed</h3>
                        <span class="text-3xl font-black text-orange-600">[VAL_HIGH]</span>
                    </div>
                    <p class="text-sm text-gray-500">[PCT_HIGH]% — Intense experiences.</p>
                </div>
                <div class="pb-6 border-b-2 border-red-500">
                    <div class="flex justify-between items-baseline mb-2">
                        <h3 class="font-bold text-gray-900 uppercase text-sm tracking-widest">Severely Stressed</h3>
                        <span class="text-3xl font-black text-red-600">[VAL_SEVERE]</span>
                    </div>
                    <p class="text-sm text-gray-500">[PCT_SEVERE]% — Extreme stress levels.</p>
                </div>
                <div class="pb-6 border-b-2 border-gray-900">
                    <div class="flex justify-between items-baseline mb-2">
                        <h3 class="font-bold text-gray-900 uppercase text-sm tracking-widest">Total Surveyed</h3>
                        <span class="text-3xl font-black text-gray-900">[VAL_TOTAL]</span>
                    </div>
                    <p class="text-sm text-gray-500">100% Valid Responses.</p>
                </div>
            </div>
        </section>

        <section id="national-benchmark" class="report-section p-10 md:p-12">
            <div class="mb-10">
                <h2 class="text-3xl font-bold text-navy mb-4 uppercase tracking-tighter">National Benchmark Comparison: <span class="text-blue-600">Student Stress Levels (India)</span></h2>
                <div class="h-1 w-24 bg-blue-600 mb-6"></div>
                <p class="text-gray-600 leading-relaxed text-lg">
                    To contextualize findings, student responses were compared against established benchmarks from the <strong>NCERT National Survey (2022)</strong> and Indian academic morbidity studies (2020–2024).
                </p>
            </div>
            <div class="mb-16">
                <h3 class="text-2xl font-bold text-navy mb-6 text-center">Stress Category Distribution: School vs. National Benchmark</h3>
                <div class="space-y-8 max-w-3xl mx-auto">
                    <div>
                        <div class="flex justify-between mb-2 text-sm font-bold uppercase tracking-widest text-gray-500">
                            <span>[SCHOOL_NAME]</span>
                            <span>Valid N=[VAL_TOTAL]</span>
                        </div>
                        <div class="flex h-12 w-full rounded-xl overflow-hidden shadow-inner">
                            <div class="bg-green-500" style="width: [PCT_BALANCED]%;" title="Balanced"></div>
                            <div class="bg-blue-500" style="width: [PCT_MILD]%;" title="Mild"></div>
                            <div class="bg-yellow-500" style="width: [PCT_MOD]%;" title="Moderate"></div>
                            <div class="bg-orange-500" style="width: [PCT_HIGH]%;" title="High"></div>
                            <div class="bg-red-500" style="width: [PCT_SEVERE]%;" title="Severe"></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="mb-12">
                <h3 class="text-2xl font-bold text-navy mb-10 text-center">Key Stress Indicator Comparison</h3>
                <div class="grid grid-cols-1 gap-8">
                    <div>
                        <div class="flex justify-between text-sm font-bold text-gray-600 mb-2">
                            <span>Exam Anxiety (Frequent Nervousness)</span>
                            <div class="flex gap-4">
                                <span class="text-blue-600">School: [PCT_ANXIETY]%</span>
                                <span class="text-gray-400">National: 81%</span>
                            </div>
                        </div>
                        <div class="chart-bar-bg">
                            <div class="chart-bar-fill bg-blue-600" style="width: [PCT_ANXIETY]%;"></div>
                            <div class="absolute top-0 bottom-0 w-1 bg-red-400 border-x border-white" style="left: 81%;"></div>
                        </div>
                    </div>
                    <div>
                        <div class="flex justify-between text-sm font-bold text-gray-600 mb-2">
                            <span>Parental Performance Pressure</span>
                            <div class="flex gap-4">
                                <span class="text-blue-600">School: [PCT_PARENT_PRESSURE]%</span>
                                <span class="text-gray-400">National: 66%</span>
                            </div>
                        </div>
                        <div class="chart-bar-bg">
                            <div class="chart-bar-fill bg-blue-600" style="width: [PCT_PARENT_PRESSURE]%;"></div>
                            <div class="absolute top-0 bottom-0 w-1 bg-red-400 border-x border-white" style="left: 66%;"></div>
                        </div>
                    </div>
                    <div>
                        <div class="flex justify-between text-sm font-bold text-gray-600 mb-2">
                            <span>Support Accessibility (Can talk to teachers/counselors)</span>
                            <div class="flex gap-4">
                                <span class="text-blue-600">School: [PCT_SUPPORT]%</span>
                                <span class="text-gray-400">National: 28%</span>
                            </div>
                        </div>
                        <div class="chart-bar-bg">
                            <div class="chart-bar-fill bg-green-500" style="width: [PCT_SUPPORT]%;"></div>
                            <div class="absolute top-0 bottom-0 w-1 bg-red-400 border-x border-white" style="left: 28%;"></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="p-10 border border-blue-50 rounded-2xl bg-blue-50/20">
                <h3 class="text-2xl font-bold text-navy mb-6">Interpretation & Insights</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-10">
                    <div class="space-y-4">
                        <div class="p-4 bg-white rounded-xl">
                            <h4 class="text-green-700 font-bold flex items-center gap-2 mb-2">Strengths vs. National Trend</h4>
                            <p class="text-sm text-gray-600 leading-relaxed">[INSIGHT_STRENGTHS]</p>
                        </div>
                    </div>
                    <div class="space-y-4">
                        <div class="p-4 bg-white rounded-xl">
                            <h4 class="text-orange-700 font-bold flex items-center gap-2 mb-2">Points of Intervention</h4>
                            <p class="text-sm text-gray-600 leading-relaxed">[INSIGHT_WEAKNESS]</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <footer class="text-center p-12 text-gray-400 text-xs mt-12">
            <div class="flex justify-center mb-8">
                <img src="https://i.ibb.co/jP5j8vf8/Screenshot-2026-01-30-at-5-16-07-PM.png" alt="Logo Small" class="h-8 grayscale opacity-30">
            </div>
            <p class="uppercase tracking-widest mb-2 font-bold">&copy; 2026 EDXSO Survey Reports</p>
            <p>[SCHOOL_NAME] — Student Assessment Experience</p>
        </footer>

    </div>
</body>
</html>
"""

# --- HELPER FUNCTIONS ---

def generate_insights_with_gemini(api_key, stats, school_name):
    if not api_key:
        return {
            "p1": "The students exhibited a diverse range of emotional responses to assessment stimuli.",
            "p2": "Detailed analysis suggests that while some students possess robust coping mechanisms, a notable segment requires targeted intervention to manage evaluation-related anxiety.",
            "key_finding": "Moderate Correlation between Preparation and Panic.",
            "conclusion": "Implementing structured mentorship programs is recommended.",
            "quote": "Success is not final, failure is not fatal: it is the courage to continue that counts.",
            "strengths": f"Support Accessibility score of {stats['support_pct']:.1f}% indicates positive teacher interaction.",
            "weaknesses": f"Exam anxiety is recorded at {stats['anxiety_pct']:.1f}%."
        }
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        ROLE: Expert Education Data Analyst.
        TASK: Write report sections for School: "{school_name}".
        DATA:
        - Total Students: {stats['count']}
        - Balanced: {stats['pct_balanced']}%
        - Mild: {stats['pct_mild']}%
        - Moderate: {stats['pct_moderate']}%
        - High: {stats['pct_high']}%
        - Severe: {stats['pct_severe']}%
        - Anxiety: {stats['anxiety_pct']}% (Nat: 81%)
        - Pressure: {stats['parent_pressure_pct']}% (Nat: 66%)
        - Support: {stats['support_pct']}% (Nat: 28%)

        OUTPUT FORMAT (JSON):
        {{
            "p1": "Exec Summary P1",
            "p2": "Exec Summary P2",
            "key_finding": "Key Finding Headline",
            "conclusion": "Conclusion sentence",
            "quote": "Inspirational quote",
            "strengths": "Insight on Strengths",
            "weaknesses": "Insight on Points of Intervention"
        }}
        """
        response = model.generate_content(prompt)
        import json
        text = response.text.replace("```json", "").replace("```", "")
        return json.loads(text)
        
    except Exception as e:
        return {
            "p1": "Analysis generation failed (Rate Limit).",
            "p2": "Try selecting fewer schools.",
            "key_finding": "Processing Complete",
            "conclusion": "Review numerical data below.",
            "quote": "Data speaks for itself.",
            "strengths": "N/A",
            "weaknesses": "N/A"
        }

def safe_generate_pdf(html_content):
    """
    Spawns a totally separate Python process to generate the PDF.
    This bypasses the Event Loop issues in Python 3.14.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as tf:
        tf.write(html_content)
        html_path = tf.name
    
    pdf_path = html_path.replace(".html", ".pdf")
    
    # NOTE: DYNAMIC HEIGHT CALCULATION SCRIPT
    script = f"""
from playwright.sync_api import sync_playwright
import sys

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(open(r"{html_path}", encoding="utf-8").read())
        
        # Calculate full body height
        body_height = page.evaluate("document.body.scrollHeight")
        
        # Add a little buffer (e.g., 50px) to ensure no cut-off
        final_height = body_height + 100
        
        # Set PDF size to fit content exactly (Single Continuous Page)
        # 1200px width covers 'max-w-5xl' nicely
        page.pdf(
            path=r"{pdf_path}", 
            width="1200px", 
            height=f"{{final_height}}px", 
            print_background=True,
            margin={{"top": "40px", "bottom": "40px", "left": "40px", "right": "40px"}}
        )
        browser.close()
except Exception as e:
    print(e)
    sys.exit(1)
"""
    
    try:
        subprocess.run([sys.executable, "-c", script], check=True, capture_output=True)
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
    except subprocess.CalledProcessError as e:
        st.error(f"PDF Gen failed: {e.stderr.decode()}")
        return None
    finally:
        # Cleanup
        if os.path.exists(html_path): os.remove(html_path)
        if os.path.exists(pdf_path): os.remove(pdf_path)
        
    return pdf_bytes

def process_data(df, api_key, selected_schools, safe_mode, output_format):
    scale_map = {'Never': 1, 'Rarely': 2, 'Sometimes': 3, 'Often': 4, 'Always': 5}
    reverse_map = {'Never': 5, 'Rarely': 4, 'Sometimes': 3, 'Often': 2, 'Always': 1}
    cols = df.columns.tolist()

    if len(cols) < 28:
        st.error("CSV format incorrect.")
        return []

    def calculate_score(row):
        score = 0
        for i in range(8, 24): score += scale_map.get(row[cols[i]], 3)
        for i in range(24, 28): score += reverse_map.get(row[cols[i]], 3)
        return score

    df['total_score'] = df.apply(calculate_score, axis=1)
    
    def get_category(s):
        if s <= 36: return 'Balanced'
        elif s <= 52: return 'Mild'
        elif s <= 68: return 'Moderate'
        elif s <= 84: return 'High'
        else: return 'Severe'
        
    df['category'] = df['total_score'].apply(get_category)

    reports = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_to_process = len(selected_schools)

    for idx, school in enumerate(selected_schools):
        status_text.text(f"Processing ({idx+1}/{total_to_process}): {school}")
        
        if safe_mode and api_key: time.sleep(4)
        
        sdf = df[df['sname'] == school]
        total = len(sdf)
        if total == 0: continue

        cats = sdf['category'].value_counts()
        stats = {
            'count': total,
            'balanced': cats.get('Balanced', 0),
            'mild': cats.get('Mild', 0),
            'moderate': cats.get('Moderate', 0),
            'high': cats.get('High', 0),
            'severe': cats.get('Severe', 0),
            'pct_balanced': round(cats.get('Balanced', 0)/total*100, 1),
            'pct_mild': round(cats.get('Mild', 0)/total*100, 1),
            'pct_moderate': round(cats.get('Moderate', 0)/total*100, 1),
            'pct_high': round(cats.get('High', 0)/total*100, 1),
            'pct_severe': round(cats.get('Severe', 0)/total*100, 1),
            'anxiety_pct': round(len(sdf[sdf[cols[8]].isin(['Often', 'Always'])]) / total * 100, 1),
            'parent_pressure_pct': round(len(sdf[sdf[cols[12]].isin(['Often', 'Always'])]) / total * 100, 1),
            'support_pct': round(len(sdf[sdf[cols[26]].isin(['Often', 'Always'])]) / total * 100, 1)
        }

        ai_content = generate_insights_with_gemini(api_key, stats, school)

        html = HTML_TEMPLATE
        replacements = {
            "[SCHOOL_NAME]": str(school),
            "[EST_YEAR]": "2024",
            "[MODE]": "Online Survey",
            "[COUNT]": str(stats['count']),
            "[EXEC_SUMMARY_P1]": ai_content.get("p1", ""),
            "[EXEC_SUMMARY_P2]": ai_content.get("p2", ""),
            "[EXEC_SUMMARY_KEY_FINDING]": ai_content.get("key_finding", ""),
            "[EXEC_SUMMARY_CONCLUSION]": ai_content.get("conclusion", ""),
            "[INSERT_KEY_QUOTE]": ai_content.get("quote", ""),
            "[INSERT_FULL_SCORING_TABLE_FROM_USER_PROMPT]": """
            <div class="grid grid-cols-5 gap-2 text-center text-xs font-medium text-gray-500">
                <div class="bg-green-100 p-2 rounded">20-36<br>Balanced</div>
                <div class="bg-blue-100 p-2 rounded">37-52<br>Mild</div>
                <div class="bg-yellow-100 p-2 rounded">53-68<br>Moderate</div>
                <div class="bg-orange-100 p-2 rounded">69-84<br>High</div>
                <div class="bg-red-100 p-2 rounded">85-100<br>Severe</div>
            </div>
            """,
            "[VAL_BALANCED]": str(stats['balanced']),
            "[PCT_BALANCED]": str(stats['pct_balanced']),
            "[VAL_MILD]": str(stats['mild']),
            "[PCT_MILD]": str(stats['pct_mild']),
            "[VAL_MOD]": str(stats['moderate']),
            "[PCT_MOD]": str(stats['pct_moderate']),
            "[VAL_HIGH]": str(stats['high']),
            "[PCT_HIGH]": str(stats['pct_high']),
            "[VAL_SEVERE]": str(stats['severe']),
            "[PCT_SEVERE]": str(stats['pct_severe']),
            "[VAL_TOTAL]": str(stats['count']),
            "[PCT_ANXIETY]": str(stats['anxiety_pct']),
            "[PCT_PARENT_PRESSURE]": str(stats['parent_pressure_pct']),
            "[PCT_SUPPORT]": str(stats['support_pct']),
            "[INSIGHT_STRENGTHS]": ai_content.get("strengths", ""),
            "[INSIGHT_WEAKNESS]": ai_content.get("weaknesses", "")
        }

        for key, val in replacements.items():
            html = html.replace(key, str(val))
            
        if output_format == "PDF":
            pdf_bytes = safe_generate_pdf(html)
            if pdf_bytes:
                reports.append((f"{school}_Report.pdf", pdf_bytes))
        else:
            reports.append((f"{school}_Report.html", html))
            
        progress_bar.progress((idx + 1) / total_to_process)

    return reports

# --- MAIN UI ---
st.title("EDXSO Report Generator: Batch Processor")
st.markdown("Generate Gold Standard Reports (HTML or Continuous PDF) with AI Analysis.")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    safe_mode = st.checkbox("Safe Mode (Rate Limit Protection)", value=True)
    output_format = st.radio("Output Format", ["HTML (Fast)", "PDF (Slow, Single Page)"])

uploaded_file = st.file_uploader("Upload Survey Data (Excel/CSV)", type=['xlsx', 'csv'])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
        
    all_schools = df['sname'].dropna().unique().tolist()
    st.success(f"Data Loaded: {len(all_schools)} schools found.")
    
    st.subheader("Batch Selection")
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_schools = st.multiselect("Select Schools:", options=all_schools, default=all_schools[:5])
    with col2:
        st.write("")
        st.write("")
        if st.button("Select All"):
            selected_schools = all_schools
    
    if st.button("Generate Reports", type="primary"):
        if not selected_schools:
            st.warning("Select at least one school.")
        else:
            with st.spinner("Processing..."):
                reports = process_data(df, api_key, selected_schools, safe_mode, output_format.split(" ")[0])
                if reports:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w") as zf:
                        for name, content in reports:
                            zf.writestr(name, content)
                    
                    st.success(f"Done! Generated {len(reports)} files.")
                    st.download_button("Download ZIP", zip_buffer.getvalue(), "school_reports.zip", "application/zip")
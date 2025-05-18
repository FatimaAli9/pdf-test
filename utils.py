import re
import textwrap
from fpdf import FPDF  # fpdf2 (after reinstalling)
import matplotlib.pyplot as plt
import os
import openai  # AI ke liye

def create_pdf(data_dict, graph_path, output_path="report_beautiful.pdf", summary_text=None):
    
    # 🔍 Check if fonts are present
    print("🗂 Font files found:", os.listdir("fonts"))

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("DejaVu", "", 12)  # Ensure font is always set

    if summary_text:
        pdf.set_font("DejaVu", "B", 14)
        pdf.set_text_color(34, 139, 34)
        pdf.cell(0, 10, "📌 AI Summary", ln=True)
        pdf.set_font("DejaVu", "", 12)
        pdf.set_text_color(0, 0, 0)
        wrapped_summary = wrap_text(summary_text)
        pdf.multi_cell(0, 8, wrapped_summary)
        pdf.ln(10)

    for k, v in data_dict.items():
        pdf.set_font("DejaVu", "B", 12)
        pdf.set_text_color(70, 130, 180)
        pdf.cell(0, 8, f"{k.strip()}:", ln=True)
        pdf.set_font("DejaVu", "", 12)
        pdf.set_text_color(0, 0, 0)
        safe_line = wrap_text(v.strip())
        pdf.multi_cell(0, 8, safe_line)
        pdf.ln(4)

    if os.path.exists(graph_path):
        pdf.ln(10)
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.set_line_width(0.5)
        pdf.rect(x-2, y-2, 185, 90)
        pdf.image(graph_path, x=x, y=y, w=180)
        pdf.ln(95)

    pdf.output(output_path)


# Extract data
def extract_data(text):
    lines = text.splitlines()
    data = [line for line in lines if ':' in line]
    return dict(line.split(':', 1) for line in data)

# Improved chart generator
def generate_graph(data, filename):
    keys = list(data.keys())
    values = []
    for v in data.values():
        try:
            values.append(float(v.strip()))
        except:
            values.append(0)

    plt.figure(figsize=(12, 6))
    bars = plt.bar(keys, values, color='#4682B4', edgecolor='black')
    plt.xticks(rotation=45, ha='right')
    plt.title("Key Metrics Overview", fontsize=16, color='#2F4F4F')
    plt.ylabel("Values", fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.05*yval, round(yval,2), ha='center', va='bottom', fontsize=10)

    plt.savefig(filename)
    plt.close()

# PDF Class with header/footer & Unicode font
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # fonts folder me ye files honi chahiye:
        # DejaVuSans.ttf, DejaVuSans-Bold.ttf, DejaVuSans-Oblique.ttf, DejaVuSans-BoldOblique.ttf
        self.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
        self.add_font("DejaVu", "B", "fonts/DejaVuSans-Bold.ttf", uni=True)
        self.add_font("DejaVu", "I", "fonts/DejaVuSans-Oblique.ttf", uni=True)
        self.add_font("DejaVu", "BI", "fonts/DejaVuSans-BoldOblique.ttf", uni=True)
        self.set_auto_page_break(auto=True, margin=15)
        self.set_font("DejaVu", "", 12)


    def header(self):
        self.set_fill_color(70, 130, 180)
        self.rect(0, 0, self.w, 20, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font("DejaVu", "", 16)
        self.cell(0, 10, "📊 Client Analysis Report", align="C", ln=True)
        self.ln(5)
        self.set_text_color(0, 0, 0)
        self.set_font("DejaVu", "", 12)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "I", 10)
        self.set_text_color(128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def force_break_long_words(text, max_word_len=50):
    def break_word(match):
        word = match.group(0)
        return "\n".join([word[i:i+max_word_len] for i in range(0, len(word), max_word_len)])
    return re.sub(r'\S{' + str(max_word_len+1) + r',}', break_word, text)

def wrap_text(text, width=90):
    text = force_break_long_words(text, max_word_len=40)
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=True, break_on_hyphens=True))

import google.generativeai as genai

def get_summary(text, gemini_api_key):
    try:
        # Step 1: Configure Gemini API key
        genai.configure(api_key=gemini_api_key)

        # Step 2: Initialize the model
        model = genai.GenerativeModel('gemini-pro')

        # Step 3: Generate content (summary)
        prompt = f"Please provide a clean and professional summary of the following client analysis:\n\n{text}"
        response = model.generate_content(prompt)

        # Step 4: Return the response text
        return response.text.strip()

    except Exception as e:
        print(f"❌ Error generating summary: {e}")
        return "Summary generation failed. Please try again."
import streamlit as st
from utils import extract_data, generate_graph, create_pdf, get_summary
import os

# Apna Gemini / OpenAI API key yahan likho
GEMINI_API_KEY = "AIzaSyBlPzg--Lz2etU1Mx5KTCvji9hGRGbMaUg"

st.title("✨ Client Analysis Report Generator")

uploaded_file = st.file_uploader("Upload your analysis text file", type=["txt"])
if uploaded_file:
    text = uploaded_file.read().decode("utf-8")
    data = extract_data(text)
    if not data:
        st.error("File format sahi nahi lag raha, data nahi mil raha.")
    else:
        st.success("Analysis data parsed!")

        # AI summary generate karo
        with st.spinner("Generating AI summary..."):
            summary = get_summary(text, GEMINI_API_KEY)
            if "failed" in summary.lower():
                st.error("❌ AI Summary failed. Please check your API key or try again.")
            else:
                st.markdown("### 🧠 AI Summary")
                st.write(summary)

        # Graph generate karo
        generate_graph(data, "graph.png")

        # PDF create karo with AI summary included
        data_with_summary = {"Summary": summary}
        data_with_summary.update(data)

        create_pdf(data_with_summary, "graph.png", output_path="final_report.pdf")

        st.success("PDF generated successfully!")
        with open("final_report.pdf", "rb") as f:
            st.download_button("Download PDF", f, file_name="Client_Report.pdf")

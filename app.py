import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from io import BytesIO
import openai
from docx import Document

# ---------------------------
# Sidebar: API key input
# ---------------------------
def set_openai_key_from_sidebar():
    st.sidebar.subheader("🔑 OpenAI API Key")
    api_key = st.sidebar.text_input(
        "Enter your OpenAI API key",
        type="password",
        help="Get a free key from https://platform.openai.com/"
    )
    if api_key:
        openai.api_key = api_key
        return api_key
    return None

api_key = set_openai_key_from_sidebar()
if not api_key:
    st.warning("⚠️ Please enter your OpenAI API key in the sidebar to continue.")
    st.info("👉 You can get a free key from OpenAI and paste it here. That way, **you pay nothing** as the app owner.")
    st.stop()

# ---------------------------
# Helpers
# ---------------------------
def extract_text_from_pdf(file):
    text = ""
    doc = fitz.open(stream=file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text("text")
    return text

def ask_openai(prompt, model="gpt-4o-mini"):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ Error: {e}"

def export_to_docx(text, title="AI Generated Report"):
    doc = Document()
    doc.add_heading(title, 0)
    doc.add_paragraph(text)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# ---------------------------
# Streamlit App
# ---------------------------
st.set_page_config(page_title="AI Genomics Assistant", layout="wide")
st.title("🧬 AI Genomics & Literature Review Assistant")

# Welcome message
st.info("""
👋 **Welcome to the AI Genomics & Literature Review Assistant!**

Here’s how to use this app:

1. 👉 Open the **sidebar on the left** (click the `>` if hidden) and enter your **OpenAI API key**.  
   - Get one free at [platform.openai.com](https://platform.openai.com/).  
   - This ensures **you don’t pay anything as the app owner**.  

2. 📄 In the **Paper Summarizer** tab:  
   - Upload one or more **PDFs** (or paste text).  
   - Choose the detail level (**Concise**, **Expanded**, or **Very Detailed – up to 30–50 pages**).  
   - Click **Summarize**.  
   - The app generates **100% humanized academic-style text** (summary, methodology, references).  
   - You can **copy-paste into Word** or **download as a Word document**.  

3. 🧬 In the **Genomic Data Interpreter** tab:  
   - Upload a **VCF**, **CSV**, or **Excel** dataset.  
   - Preview your data instantly.  
   - Click **Interpret Genomic Data** for AI-generated insights.  

⚡ That’s it! Instant insights for research papers and genomics data — ready to use in your reports.
""")

tabs = st.tabs(["📄 Paper Summarizer", "🧬 Genomic Data Interpreter"])

# ---------------------------
# Tab 1: Paper Summarizer
# ---------------------------
with tabs[0]:
    st.header("Research Paper / Abstract Summarizer")

    uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])
    user_text = st.text_area("Or paste text here:")

    detail_level = st.radio(
        "Detail level",
        ["Concise", "Expanded", "Very Detailed (30–50 pages)"],
        horizontal=True
    )

    if st.button("Summarize"):
        text = ""
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(uploaded_file)
            else:
                text = uploaded_file.read().decode("utf-8")
        elif user_text.strip():
            text = user_text.strip()

        if not text:
            st.error("❌ Please upload a file or paste some text.")
        else:
            prompt = f"""
            You are an AI assistant. Read the following paper text and generate a {detail_level} research-style report.
            Include:
            - Structured summary
            - Rewritten methodology
            - Interpretation of figures/tables if present
            - Proper academic-style references

            Text:
            {text}
            """
            result = ask_openai(prompt)
            st.success("✅ Generated Summary:")
            st.write(result)

            # Offer Word download
            docx_file = export_to_docx(result, "AI Generated Literature Review")
            st.download_button(
                "⬇️ Download as Word Document",
                data=docx_file,
                file_name="AI_Genomics_Report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

# ---------------------------
# Tab 2: Genomic Data Interpreter
# ---------------------------
with tabs[1]:
    st.header("Upload Genomic Dataset (VCF / CSV / Excel)")
    gfile = st.file_uploader("Choose a file", type=["vcf","csv","xlsx"])

    if gfile is not None:
        df = None
        if gfile.name.endswith(".csv"):
            df = pd.read_csv(gfile)
        elif gfile.name.endswith(".xlsx"):
            df = pd.read_excel(gfile)
        elif gfile.name.endswith(".vcf"):
            content = gfile.read().decode("utf-8")
            rows = [line.split("\t") for line in content.splitlines() if not line.startswith("##")]
            df = pd.DataFrame(rows[1:], columns=rows[0])
        else:
            st.error("Unsupported file format")
            df = None

        if df is not None:
            st.write("📊 Preview of uploaded dataset:")
            st.dataframe(df.head())

            if st.button("Interpret Genomic Data"):
                prompt = f"""
                You are a genomics assistant. Interpret this dataset (first 20 rows shown):

                {df.head(20).to_csv(index=False)}

                Provide:
                - Summary of key findings
                - Possible biological/clinical interpretations
                - Limitations and cautions
                """
                result = ask_openai(prompt)
                st.success("✅ Genomic Interpretation:")
                st.write(result)


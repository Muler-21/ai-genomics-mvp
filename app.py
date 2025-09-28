import streamlit as st
import openai
import os
import tempfile
from PyPDF2 import PdfReader

# ------------------------------
# Sidebar: API Key Input
# ------------------------------
st.sidebar.header("🔑 OpenAI API Key")
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")

if api_key:
    openai.api_key = api_key
else:
    st.warning("⚠️ Please enter your OpenAI API key in the sidebar to continue.")
    st.stop()

# ------------------------------
# App Title + Banner
# ------------------------------
st.image("banner.png", use_column_width=True)

st.title("🧬 AI Genomics & Literature Review")
st.markdown(
    "### Summarize. Rewrite. Interpret.  \n"
    "Upload research papers (PDF) or text, and get **humanized summaries and reviews** powered by AI."
)

# ------------------------------
# PDF Upload
# ------------------------------
uploaded_files = st.file_uploader(
    "📄 Upload up to 10 research papers (PDF)",
    type=["pdf"],
    accept_multiple_files=True
)

def extract_text_from_pdf(uploaded_file):
    """Extracts text from a PDF file."""
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text.strip()

def summarize_text(text, api_key):
    """Generates a summary using OpenAI chat completion."""
    try:
        client = openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an academic writing assistant. Summarize text into clear, human-like prose with proper citations where applicable."},
                {"role": "user", "content": text}
            ],
            temperature=0.7,
            max_tokens=800
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ------------------------------
# Summarization
# ------------------------------
if uploaded_files:
    if st.button("✨ Summarize All Papers"):
        for file in uploaded_files:
            with st.spinner(f"Processing {file.name}..."):
                text = extract_text_from_pdf(file)

                if not text:
                    st.error(f"❌ Could not extract text from {file.name}")
                    continue

                summary = summarize_text(text, api_key)

                st.subheader(f"📑 Summary for {file.name}")
                st.write(summary)
else:
    st.info("📌 Upload 1–10 PDFs to begin summarizing.")


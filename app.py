import streamlit as st
import fitz  # PyMuPDF for PDF text extraction
import openai
import os

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="AI Genomics & Literature Review",
    page_icon="🧬",
    layout="wide"
)

# ---------------------------
# Banner & Title
# ---------------------------
st.image("banner.png", use_column_width=True)
st.title("🧬 AI Genomics & Literature Review")
st.markdown("**Summarize. Rewrite. Interpret.** — Your AI-powered assistant for genomics and literature reviews.")

# ---------------------------
# API Key Handling
# ---------------------------
api_key = st.sidebar.text_input("🔑 Enter your OpenAI API Key", type="password")
if not api_key:
    st.warning("⚠️ Please enter your OpenAI API key in the sidebar to continue.")
    st.stop()

openai.api_key = api_key

# ---------------------------
# Tabs
# ---------------------------
tab1, tab2 = st.tabs(["📄 Paper Summarizer", "🧬 Genomic Data Interpreter"])

# ---------------------------
# 📄 Paper Summarizer
# ---------------------------
with tab1:
    st.header("Research Paper / Abstract Summarizer")

    uploaded_files = st.file_uploader(
        "Upload up to 10 PDF or TXT files",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )

    if uploaded_files:
        all_texts = []
        for uploaded_file in uploaded_files:
            if uploaded_file.type == "application/pdf":
                pdf_doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                text = ""
                for page in pdf_doc:
                    text += page.get_text()
                all_texts.append(text)
            else:
                all_texts.append(uploaded_file.read().decode("utf-8"))

        combined_text = "\n".join(all_texts)

        if st.button("Summarize All Papers"):
            with st.spinner("Generating summary..."):
                try:
                    response = openai.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are an expert scientific writer. Summarize multiple research papers into one coherent literature review. Humanize the text, ensure clarity, and include citations when available."},
                            {"role": "user", "content": combined_text}
                        ],
                        max_tokens=3000,
                        temperature=0.7
                    )
                    st.success("✅ Summary generated successfully!")
                    st.write(response.choices[0].message.content)

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ---------------------------
# 🧬 Genomic Data Interpreter
# ---------------------------
with tab2:
    st.header("Upload Genomic Dataset (VCF / CSV / Excel)")
    file = st.file_uploader("Choose a file", type=["vcf", "csv", "xlsx"])

    if file:
        st.info("Genomic interpretation is in development. Future versions will provide AI-driven analysis of variants and expression data.")


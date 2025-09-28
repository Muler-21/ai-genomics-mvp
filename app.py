
import os
import io
import pandas as pd
import streamlit as st

# --- OpenAI (legacy v0.28+ style import) ---
import openai

# Read API key from env var (recommended)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

st.set_page_config(page_title="AI Genomics MVP", layout="wide")
st.title("🧬 AI Genomics MVP")
st.caption("Upload simple genomics data or paste a paper to get an AI-generated interpretation.")

# Helper: safe OpenAI chat call
def ai_chat(prompt, system="You are a helpful bioinformatics assistant."):
    if not OPENAI_API_KEY:
        return "⚠️ OPENAI_API_KEY is not set. Please export it in your shell before running Streamlit."
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":system},
                {"role":"user","content":prompt}
            ],
            max_tokens=700,
            temperature=0.2,
        )
        return resp["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ OpenAI error: {e}"

tab1, tab2 = st.tabs(["📄 Paper Summarizer", "🧬 Genomic Data Interpreter"])

with tab1:
    st.subheader("📄 Research Paper / Abstract Summarizer")
    txt = st.text_area("Paste an abstract or paper text:", height=250, placeholder="Paste text here...")
    if st.button("Summarize", key="summarize_btn"):
        if txt.strip():
            with st.spinner("Summarizing..."):
                prompt = f"Summarize the following research text in sections: Objectives, Methods, Results, Conclusions. Keep it concise and structured.\n\n{txt}"
                out = ai_chat(prompt, system="You summarize scientific papers in a structured, precise style.")
            st.markdown("### 🧾 Summary")
            st.write(out)
        else:
            st.warning("Please paste some text first.")

with tab2:
    st.subheader("🧬 Upload Genomic Dataset (VCF / CSV / Excel)")
    f = st.file_uploader("Choose a file", type=["vcf","csv","xlsx"])

    def parse_vcf(file_bytes):
        text = file_bytes.decode("utf-8", errors="ignore")
        lines = [ln for ln in text.splitlines() if ln.strip()]
        header_cols = []
        data_rows = []
        for ln in lines:
            if ln.startswith("#CHROM"):
                header_cols = ln.lstrip("#").split("\t")
            elif ln.startswith("#"):
                continue
            else:
                parts = ln.split("\t")
                if header_cols and len(parts) >= len(header_cols):
                    data_rows.append(parts[:len(header_cols)])
        if header_cols and data_rows:
            import pandas as pd
            df = pd.DataFrame(data_rows, columns=header_cols)
            return df
        else:
            # fallback minimal columns for preview
            df = pd.DataFrame({"raw_line":[ln for ln in lines if not ln.startswith("#")]})
            return df

    if f is not None:
        ext = f.name.split(".")[-1].lower()
        df = None
        try:
            if ext == "csv":
                df = pd.read_csv(f)
            elif ext == "xlsx":
                df = pd.read_excel(f)
            elif ext == "vcf":
                file_bytes = f.read()
                df = parse_vcf(file_bytes)
        except Exception as e:
            st.error(f"Failed to read file: {e}")

        if df is not None:
            st.markdown("#### 📊 Preview (first 20 rows)")
            st.dataframe(df.head(20), use_container_width=True)

            # Lightweight feature extraction for prompt
            col_names = list(df.columns)
            head_csv = df.head(30).to_csv(index=False)

            # Try to extract obvious gene, chrom, pos columns if present
            candidate_cols = [c for c in col_names if c.lower() in ["gene","genes","symbol","gene_symbol","chrom","chromosome","pos","position","ref","alt"]]
            detected_cols = candidate_cols[:6]

            st.markdown("#### ⚙️ Detected columns (heuristic)")
            if detected_cols:
                st.write(", ".join(detected_cols))
            else:
                st.write("None detected (will use the table head as context).")

            if st.button("Interpret Dataset with AI", key="interpret_btn"):
                with st.spinner("Interpreting..."):
                    prompt = f"""You are a genomic scientist. Based on the following tabular sample (CSV) from a genomic dataset, provide:
- What the dataset likely represents
- Key features/columns of interest
- Notable variants/genes if any are visible
- Potential biological/clinical significance (high-level, not medical advice)
- Recommended next analysis steps (e.g., variant annotation, filtering, visualization, QC)

Table sample (first rows):
{head_csv}

If relevant, organize the answer with bullet points and short paragraphs.
"""
                    out = ai_chat(prompt, system="You are a precise, safety-aware bioinformatics expert. You never provide medical advice; you only suggest research-oriented next steps.")
                st.markdown("### 🧾 AI Interpretation")
                st.write(out)

        else:
            st.info("Upload a valid VCF, CSV, or XLSX file to preview and interpret.")
    else:
        st.caption("Supports VCF for variants and CSV/XLSX for tabular results (e.g., annotations, counts).")

st.markdown("---")
st.caption("Tip: Set your OPENAI_API_KEY env var before running. This is a minimal MVP for experimentation, not a clinical tool.")

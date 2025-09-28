
# AI Genomics MVP (Streamlit)

A tiny MVP you can run locally: summarize research text and interpret simple genomics datasets (VCF/CSV/XLSX) with an AI prompt.

## 1) Prereqs (Ubuntu Bash)
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
python3 --version
pip3 --version
```

## 2) Create a Project Folder & Virtual Env
```bash
mkdir -p ~/ai-genomics-mvp
cd ~/ai-genomics-mvp
python3 -m venv .venv
source .venv/bin/activate
```

> To leave the env later: `deactivate`

## 3) Copy Files Into the Folder
Download `app.py` and `requirements.txt` from ChatGPT and place them in this folder.

## 4) Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 5) Set Your OpenAI API Key
```bash
export OPENAI_API_KEY="sk-REPLACE_WITH_YOUR_KEY"
# Optional: make it persistent
echo 'export OPENAI_API_KEY="sk-REPLACE_WITH_YOUR_KEY"' >> ~/.bashrc
source ~/.bashrc
```

## 6) Run the App
```bash
streamlit run app.py
```
Then open the local URL shown in the terminal (usually http://localhost:8501).

## Notes
- This MVP uses a legacy OpenAI call signature via `openai==0.28.1`. If you prefer the new SDK, adapt the code accordingly.
- Keep this for research/educational purposes—**not** clinical use.
- If you upload very large files, consider adding server-side size checks and pagination.

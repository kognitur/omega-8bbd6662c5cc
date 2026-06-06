import streamlit as st
import pandas as pd
import re
from io import StringIO
import csv

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else ''

def extract_phone(text):
    patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return ''

def extract_linkedin(text):
    match = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
    return 'https://' + match.group(0) if match else ''

def extract_name(text):
    lines = text.strip().split('\n')
    for line in lines[:5]:
        line = line.strip()
        if line and not any(x in line.lower() for x in ['@', 'linkedin', 'phone', 'mobile', 'tel', 'email']):
            words = line.split()
            if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w[0].isalpha()):
                return line
    return ''

def extract_title(text):
    lines = text.strip().split('\n')
    for i, line in enumerate(lines):
        if extract_name(text) and extract_name(text) in line:
            continue
        if line.strip() and not any(x in line.lower() for x in ['@', 'linkedin', 'phone', 'mobile', 'tel', 'email', 'http']):
            words = line.split()
            if 1 <= len(words) <= 6 and any(w[0].isupper() for w in words if w[0].isalpha()):
                return line.strip()
    return ''

def process_signature(text):
    return {
        'name': extract_name(text),
        'title': extract_title(text),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'linkedin': extract_linkedin(text)
    }

st.set_page_config(page_title="Email Signature Extractor", page_icon="📧")
st.title("📧 Email Signature Extractor")
st.markdown("Paste email signatures below or upload a CSV file with signatures.")

uploaded_file = st.file_uploader("Upload CSV file (optional)", type=['csv'])
input_text = st.text_area("Or paste email signatures here (one per line, separated by ---):", height=200)

results = []

if uploaded_file:
    try:
        content = uploaded_file.read().decode('utf-8')
        signatures = [s.strip() for s in content.split('\n') if s.strip()]
        for sig in signatures:
            results.append(process_signature(sig))
        st.success(f"Processed {len(results)} signatures from file.")
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")

if input_text:
    signatures = re.split(r'\n---\n|\n---|---\n', input_text)
    for sig in signatures:
        if sig.strip():
            results.append(process_signature(sig.strip()))

if results:
    df = pd.DataFrame(results)
    st.subheader("Extracted Signatures")
    st.dataframe(df, use_container_width=True)
    
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="Download CSV",
        data=csv_buffer.getvalue(),
        file_name="extracted_signatures.csv",
        mime="text/csv"
    )
else:
    if uploaded_file or input_text:
        st.warning("No signatures could be extracted. Please check your input.")
    else:
        st.info("Paste signatures or upload a file to get started.")

st.markdown("---")
st.markdown("**Tips:**")
st.markdown("- Separate multiple signatures with `---`")
st.markdown("- Upload a CSV with one signature per row")
st.markdown("- Works best with standard email signature formats")
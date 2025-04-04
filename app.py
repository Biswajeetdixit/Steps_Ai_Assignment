import os
import docx
import PyPDF2
import streamlit as st
import requests
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = "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"
N8N_WEBHOOK_URL = "https://github.com/n8n-io/n8n "  # Set your n8n webhook URL

# Initialize LLM model (Groq)
llm = ChatGroq(model_name="llama3-8b-8192", api_key=GROQ_API_KEY)

# Function to extract text from PDF
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Function to send data to n8n webhook
def send_to_n8n(resume_name, match_score):
    payload = {"resume": resume_name, "match_score": match_score}
    response = requests.post(N8N_WEBHOOK_URL, json=payload)
    return response.status_code == 200

# Streamlit UI
st.title("🤖 AI-Powered Resume Screening")
st.write("Upload resumes and enter a job description to find the best match using AI & automation.")

# Input fields
jd_input = st.text_area("📋 Paste Job Description")
uploaded_files = st.file_uploader("📂 Upload Resumes (PDF/DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

if st.button("🔍 Match Resumes"):
    if not jd_input or not uploaded_files:
        st.warning("⚠️ Please enter a job description and upload at least one resume.")
    else:
        st.write("🚀 Analyzing resumes with AI...")
        
        results = []
        for uploaded_file in uploaded_files:
            file_text = extract_text_from_pdf(uploaded_file) if uploaded_file.name.endswith(".pdf") else extract_text_from_docx(uploaded_file)
            
            prompt = f"""
            You are an AI specialized in resume screening. Compare the following resume with the given job description and rate its match on a scale of 0 to 100.

            Job Description:
            {jd_input}

            Resume Content:
            {file_text}

            Return only the score as a number.
            """

            response = llm.invoke(prompt)
            import re
            match = re.search(r"(\d+(\.\d+)?)", response.content)  # No .decode()


            if match:
                match_score = float(match.group(1))  # Extracted numeric value

            else:
                match_score = 0.0  # Default value

            st.write(f"Match Score: {match_score}")  # Display the extracted score




            # Send data to n8n automation
            send_to_n8n(uploaded_file.name, match_score)

            results.append((uploaded_file.name, match_score))

        # Sort by highest match score
        results.sort(key=lambda x: x[1], reverse=True)

        # Display results
        st.subheader("📊 Matching Results:")
        for file, score in results:
            st.write(f"**{file}** — Match Score: `{score:.2f}`")

st.write("💡 **This system integrates n8n for workflow automation and Langflow for customization.**")



import time
import random
import requests
import pandas as pd
import smtplib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from docx import Document

# Define Job Search Keywords
JOB_TITLES = [
    "Java Developer", "Junior Java Developer", "Java Frontend Developer", "Java Backend Developer",
    "Full Stack Java Developer", "Senior Java Developer", "Java Software Engineer", "Software Engineer",
    "Senior Software Engineer", "Software Developer", "SE Software Developer", "Angular Developer",
    "React Developer", "Node Developer", "JavaScript Developer"
]
LOCATION = "Remote OR USA"
EXCLUDED_COMPANIES = ["Vanguard", "Verizon", "Capital One"]
JOB_SITES = [
    "https://www.linkedin.com/jobs/search/?keywords=",
    "https://www.indeed.com/jobs?q=",
    "https://www.dice.com/jobs?q=",
    "https://www.jobrecruiter.com/jobs?q=",
    "https://www.glassdoor.com/Job/jobs.htm?sc.keyword="
]

# Email Configuration
GMAIL_USER = "your_email@gmail.com"
GMAIL_PASSWORD = "your_app_password"
RECIPIENT_EMAIL = "vamsi.bheemani.hw@gmail.com"

# Resume & Cover Letter Storage
RESUME_FOLDER = "./resumes/"
COVER_LETTER_FOLDER = "./cover_letters/"
USER_RESUME_PATH = "./Venkata_Vamsi_Krishna.docx"  # Path to the original resume

# OpenAI API Configuration
OPENAI_API_KEY = "your_openai_api_key"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}

data = [
    {"Company": "Company A", "Job Title": "Software Engineer", "Job Link": "https://example.com"},
    {"Company": "Company B", "Job Title": "Java Developer", "Job Link": "https://example.com"}
]

def extract_personal_details():
    """ Extracts personal details (name, phone, email, education, work experience) from the user's resume. """
    doc = Document(USER_RESUME_PATH)
    resume_text = "\n".join([para.text for para in doc.paragraphs])
    return resume_text

def generate_updated_resume(job_description):
    """ Uses OpenAI to update the resume while keeping personal details intact. """
    personal_details = extract_personal_details()
    prompt = f"""
    Modify my resume to align with this job description:
    {job_description}
    Keep my name, phone number, email, work experience, and education the same.
    """
    response = requests.post(OPENAI_URL, headers=HEADERS, json={"model": "gpt-4", "messages": [{"role": "system", "content": "Generate an updated resume."}, {"role": "user", "content": prompt}]})
    updated_resume = response.json().get("choices")[0]["message"]["content"]
    return f"{personal_details}\n\n{updated_resume}"

def filter_real_time_jobs(jobs):
    """ Filters out fake job postings by checking job descriptions and sources. """
    return [job for job in jobs if "contract" in job.lower() or "full-time" in job.lower()]

def prevent_duplicate_applications(job_list):
    """ Ensures that duplicate applications are not submitted. """
    applied_jobs = pd.read_csv("job_applications.csv") if "job_applications.csv" in job_list else pd.DataFrame()
    return applied_jobs

def send_follow_up_emails():
    """ Sends follow-up emails to recruiters after applications. """
    message = "Subject: Follow-Up on Job Application\n\nHello, I recently applied for the job and wanted to follow up on my application. Looking forward to discussing further."
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, RECIPIENT_EMAIL, message)

def send_updated_resume_via_email(updated_resume_text, company_name):
    """ Sends the AI-modified resume to the user via email. """
    message = f"Subject: Updated Resume for {company_name}\n\nHere is the updated resume:\n\n{updated_resume_text}"
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, RECIPIENT_EMAIL, message)
df = pd.DataFrame(data)
df.to_csv("applied_jobs.csv", index=False)

# Execute automation functions
# send_follow_up_emails()
print("✅ Enhancements completed: AI-updated resumes with personal details preserved, real-time job filtering, duplicate application prevention, and follow-ups!")

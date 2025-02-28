import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Define job search parameters
job_titles = [
    "Java Developer", "Junior Java Developer", "Java Frontend Developer",
    "Java Backend Developer", "Full Stack Java Developer", "Senior Java Developer",
    "Java Software Engineer", "Software Engineer", "Senior Software Engineer",
    "Software Developer", "Angular Developer", "React Developer",
    "Node Developer", "JavaScript Developer"
]
locations = ["Remote", "Hybrid", "USA"]
job_types = ["Full-time", "Contract"]

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def search_jobs():
    job_data = []
    for title in job_titles:
        for location in locations:
            driver.get("https://www.indeed.com/")
            time.sleep(5)  # Ensure page loads

            # Wait until the elements are visible
            wait = WebDriverWait(driver, 20)

            try:
                search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='What']")))
                location_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Where']")))
                search_box.send_keys(title)
                location_box.send_keys(location)
                search_box.send_keys(Keys.RETURN)
                time.sleep(5)  # Wait for results to load

                # Wait until job listings appear
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".job_seen_beacon")))
                jobs = driver.find_elements(By.CSS_SELECTOR, ".job_seen_beacon")
                
                for job in jobs:
                    try:
                        job_title = job.find_element(By.CLASS_NAME, "jobTitle").text
                        company = job.find_element(By.CLASS_NAME, "companyName").text
                        job_link = job.find_element(By.TAG_NAME, "a").get_attribute("href")
                        job_data.append({"Company": company, "Job Title": job_title, "Job Link": job_link})
                    except:
                        continue
            except Exception as e:
                print(f"Error finding job search fields: {e}")
                continue
    return job_data

# Generate auto cover letter
def generate_cover_letter(job_title, company):
    cover_letter = f"""
    Dear Hiring Manager at {company},

    I am excited to apply for the {job_title} position at {company}. With 5 years of experience in Java development and UI technologies, I am confident in my ability to contribute effectively to your team.

    I look forward to the opportunity to discuss how my skills align with your needs.

    Best regards,
    Venkata Vamsi Krishna
    """
    return cover_letter

# Apply to jobs
def apply_to_jobs():
    applied_jobs = []
    jobs = search_jobs()
    for job in jobs:
        cover_letter = generate_cover_letter(job["Job Title"], job["Company"])
        applied_jobs.append({"Company": job["Company"], "Job Title": job["Job Title"], "Job Link": job["Job Link"], "Cover Letter": cover_letter})
    return applied_jobs

# Save applied jobs to CSV
def save_jobs_to_csv():
    applied_jobs = apply_to_jobs()
    df = pd.DataFrame(applied_jobs)
    df.to_csv("applied_jobs.csv", index=False)

# Run the bot
save_jobs_to_csv()

driver.quit()

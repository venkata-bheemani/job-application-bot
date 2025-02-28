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

# Job search platforms
job_platforms = {
    "Indeed": "https://www.indeed.com/",
    "LinkedIn": "https://www.linkedin.com/jobs/",
    "Dice": "https://www.dice.com/jobs",
    "Glassdoor": "https://www.glassdoor.com/Job"
}

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def search_jobs():
    job_data = []
    for platform, url in job_platforms.items():
        for title in job_titles:
            for location in locations:
                driver.get(url)
                time.sleep(5)  # Ensure page loads

                # Wait until the elements are visible
                wait = WebDriverWait(driver, 20)

                try:
                    if platform == "Indeed":
                        search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='What']")))
                        location_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Where']")))
                    elif platform == "LinkedIn":
                        search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.jobs-search-box__text-input")))
                        location_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.jobs-search-box__text-input[aria-label='City, state, or zip code']")))
                    elif platform == "Dice":
                        search_box = wait.until(EC.presence_of_element_located((By.ID, "typeaheadInput")))
                        location_box = wait.until(EC.presence_of_element_located((By.ID, "google-location-search")))
                    elif platform == "Glassdoor":
                        search_box = wait.until(EC.presence_of_element_located((By.ID, "KeywordSearch")))
                        location_box = wait.until(EC.presence_of_element_located((By.ID, "LocationSearch")))
                    else:
                        continue

                    search_box.send_keys(title)
                    location_box.send_keys(location)
                    search_box.send_keys(Keys.RETURN)
                    time.sleep(5)  # Wait for results to load

                    try:
                        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".job_seen_beacon, .job-card-container, .card, .jobListing")))
                        if platform == "Indeed":
                            jobs = driver.find_elements(By.CSS_SELECTOR, ".job_seen_beacon")
                        elif platform == "LinkedIn":
                            jobs = driver.find_elements(By.CSS_SELECTOR, ".job-card-container")
                        elif platform == "Dice":
                            jobs = driver.find_elements(By.CSS_SELECTOR, ".card")
                        elif platform == "Glassdoor":
                            jobs = driver.find_elements(By.CSS_SELECTOR, ".jobListing")
                        else:
                            jobs = []
                    except Exception as e:
                        print(f"⚠ No jobs found on {platform}. The selector might need updating: {e}")
                        jobs = []

                    if not jobs:
                        print(f"⚠ No job listings found on {platform} for {title} in {location}.")

                    for job in jobs:
                        try:
                            job_title = job.find_element(By.CLASS_NAME, "jobTitle").text
                            company = job.find_element(By.CLASS_NAME, "companyName").text
                            job_link_element = job.find_element(By.TAG_NAME, "a")
                            job_link = job_link_element.get_attribute("href") if job_link_element else "No Link"

                            print(f"✔ Found job: {job_title} at {company} on {platform}")
                            job_data.append({"Platform": platform, "Company": company, "Job Title": job_title, "Job Link": job_link})
                        except Exception as e:
                            print(f"⚠ Error extracting job details on {platform}: {e}")
                except Exception as e:
                    print(f"Error finding job search fields on {platform}: {e}")
                    continue
    return job_data

# Apply to jobs
def apply_to_jobs():
    applied_jobs = []
    jobs = search_jobs()
    if not jobs:
        print("⚠ No jobs found. Please check if job search fields and selectors are correct.")
    for job in jobs:
        print(f"Applying for: {job['Job Title']} at {job['Company']} ({job['Platform']})")
        applied_jobs.append(job)
    return applied_jobs

# Save applied jobs to CSV
def save_jobs_to_csv():
    applied_jobs = apply_to_jobs()
    if not applied_jobs:
        print("⚠ No jobs were applied to. Ensure job listings are being extracted correctly.")
    df = pd.DataFrame(applied_jobs)
    df.to_csv("applied_jobs.csv", index=False)
    print(f"✅ Job applications saved to applied_jobs.csv ({len(applied_jobs)} jobs applied).")

# Run the bot
save_jobs_to_csv()

driver.quit()

import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Load credentials from GitHub Secrets
DICE_USERNAME = os.getenv("DICE_USERNAME")
DICE_PASSWORD = os.getenv("DICE_PASSWORD")

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Define job search parameters
job_titles = ["Java Developer"]
locations = ["Remote", "Hybrid", "Onsite", "USA"]

# Dice Login URL
DICE_LOGIN_URL = "https://www.dice.com/dashboard/login"
DICE_SEARCH_URL = "https://www.dice.com/jobs"

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def login_to_dice():
    driver.get(DICE_LOGIN_URL)
    time.sleep(5)  # Wait for page to load
    
    try:
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email")))
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        
        email_field.send_keys(DICE_USERNAME)
        password_field.send_keys(DICE_PASSWORD)
        login_button.click()
        time.sleep(5)
        print("✅ Successfully logged into Dice!")
    except Exception as e:
        print(f"❌ Login failed: {e}")

def search_and_apply_jobs():
    applied_jobs = []
    driver.get(DICE_SEARCH_URL)
    time.sleep(5)  # Ensure page loads

    for title in job_titles:
        for location in locations:
            try:
                search_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "typeaheadInput")))
                location_box = driver.find_element(By.ID, "google-location-search")
                
                search_box.clear()
                location_box.clear()
                search_box.send_keys(title)
                location_box.send_keys(location)
                search_box.send_keys(Keys.RETURN)
                time.sleep(5)  # Wait for results
                
                job_listings = driver.find_elements(By.CSS_SELECTOR, ".card")
                if not job_listings:
                    print(f"⚠ No jobs found for {title} in {location}")
                    continue
                
                for job in job_listings[:5]:  # Limit applications per search
                    try:
                        job_title = job.find_element(By.CLASS_NAME, "card-title-link").text
                        company = job.find_element(By.CLASS_NAME, "card-company").text
                        job_link = job.find_element(By.TAG_NAME, "a").get_attribute("href")
                        
                        print(f"✔ Found job: {job_title} at {company}")
                        
                        # Apply to job
                        driver.get(job_link)
                        time.sleep(5)
                        try:
                            apply_button = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Apply Now')]")
                            ))
                            apply_button.click()
                            time.sleep(3)
                            print(f"🚀 Successfully applied to {job_title} at {company}")
                            applied_jobs.append({"Company": company, "Job Title": job_title, "Job Link": job_link})
                        except:
                            print(f"⚠ Could not apply to {job_title} at {company}")
                    except Exception as e:
                        print(f"⚠ Error extracting job details: {e}")
            except Exception as e:
                print(f"Error searching jobs: {e}")
    return applied_jobs

def save_jobs_to_csv():
    applied_jobs = search_and_apply_jobs()
    df = pd.DataFrame(applied_jobs)
    df.to_csv("applied_jobs.csv", index=False)
    print(f"✅ Job applications saved to applied_jobs.csv ({len(applied_jobs)} jobs applied).")

# Run the bot
login_to_dice()
save_jobs_to_csv()

driver.quit()

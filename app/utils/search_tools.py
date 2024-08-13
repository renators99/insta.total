import re
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import os
import json

def calculate_dates(option, days_per_period=30):
    today = datetime.today()
    start_date = today - timedelta(days=days_per_period * option)
    end_date = today - timedelta(days=days_per_period * (option - 1))
    return start_date.strftime('%m/%d/%Y'), end_date.strftime('%m/%d/%Y')

def search_on_google(driver, search_term):
    driver.get("https://www.google.com")
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )
    query = f"{search_term} site:instagram.com"
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "search"))
    )

def apply_filters(driver, date_option):
    tools_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.BaegVc.YmvwI#hdtb-tls"))
    )
    tools_button.click()
    
    advanced_search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Búsqueda avanzada')]"))
    )
    advanced_search_button.click()

    region_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@id='cr_button']"))
    )
    region_button.click()
    us_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//li[@value='countryUS']//div[contains(text(), 'Estados Unidos')]"))
    )
    us_option.click()

    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@value='Búsqueda avanzada']"))
    )
    search_button.click()

    any_date_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'De cualquier fecha')]"))
    )
    any_date_button.click()

    customize_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[@role='menuitem' and contains(text(), 'Personalizar...')]"))
    )
    customize_button.click()

    start_date, end_date = calculate_dates(date_option)
    start_date_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "OouJcb"))
    )
    end_date_input = driver.find_element(By.ID, "rzG2be")
    start_date_input.send_keys(start_date)
    end_date_input.send_keys(end_date)

    go_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//g-button[contains(@class, 'Ru1Ao BwGU8e fE5Rge')]"))
    )
    go_button.click()

def extract_links(driver):
    all_hrefs = []
    while True:
        div_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.dURPMd"))
        )
        
        result_links = div_element.find_elements(By.XPATH, ".//a[@href and contains(@href, 'instagram.com')]")
        hrefs = [link.get_attribute("href") for link in result_links]
        all_hrefs.extend(hrefs)

        for href in hrefs:
            print(href)
        
        try:
            next_button = driver.find_element(By.ID, "pnnext")
            next_button.click()
            time.sleep(1)
        except:
            print("The 'Next' button was not found or there are no more pages.")
            break

    return all_hrefs

def extract_result_count(driver):
    result_stats = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "result-stats"))
    )
    result_text = result_stats.text
    match = re.search(r"Cerca de ([\d,]+) resultados", result_text)
    if match:
        result_count_str = match.group(1).replace(",", "")
        result_count = int(result_count_str)
        print(f"Approximate result count: {result_count}")
    else:
        print("Could not extract the number of results.")
        result_count = 0
    return result_count

def save_json(result_json, search_term, start_date, end_date):
    os.makedirs('data', exist_ok=True)
    filename = f"data/results_{search_term}_{start_date.replace('/', '-')}_{end_date.replace('/', '-')}.json"
    with open(filename, 'w') as file:
        json.dump(result_json, file, indent=4)
    return filename

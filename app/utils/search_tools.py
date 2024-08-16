import re
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from datetime import datetime, timedelta
from fastapi import HTTPException  # Asegúrate de que esta línea esté presente
import os
import json

def calculate_dates(option, days_per_period=30):
    today = datetime.today()
    start_date = today - timedelta(days=days_per_period * option)
    end_date = today - timedelta(days=days_per_period * (option - 1))
    return start_date.strftime('%m/%d/%Y'), end_date.strftime('%m/%d/%Y')

def search_on_google(driver, search_term):
    driver.get("https://www.google.com")
    check_for_captcha(driver, "Google Search Initialization")
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )
    query = f"{search_term} site:instagram.com"
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "search"))
    )
    check_for_captcha(driver, "Search Results")

def apply_filters(driver, date_option):
    try:
        tools_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.BaegVc.YmvwI#hdtb-tls"))
        )
        tools_button.click()
        check_for_captcha(driver, "Tools Button Click")
    except TimeoutException as te:
        raise HTTPException(status_code=504, detail="Timeout occurred while waiting for the 'Tools' button.") from te
    except NoSuchElementException as nse:
        raise HTTPException(status_code=404, detail="The 'Tools' button was not found.") from nse
    except WebDriverException as we:
        raise HTTPException(status_code=500, detail="WebDriver encountered an error while clicking the 'Tools' button.") from we

    try:
        advanced_search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Búsqueda avanzada') or contains(text(), 'Advanced search')]"))
        )
        advanced_search_button.click()
        check_for_captcha(driver, "Advanced Search Button Click")
    except TimeoutException as te:
        raise HTTPException(status_code=504, detail="Timeout occurred while waiting for the 'Advanced Search' button.") from te
    except NoSuchElementException as nse:
        raise HTTPException(status_code=404, detail="The 'Advanced Search' button was not found.") from nse
    except WebDriverException as we:
        raise HTTPException(status_code=500, detail="WebDriver encountered an error while clicking the 'Advanced Search' button.") from we

    try:
        region_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='cr_button']"))
        )
        region_button.click()
        us_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[@value='countryUS']//div[contains(text(), 'Estados Unidos') or contains(text(), 'United States')]"))
        )
        us_option.click()
    except TimeoutException as te:
        raise HTTPException(status_code=504, detail="Timeout occurred while selecting the region filter.") from te
    except NoSuchElementException as nse:
        raise HTTPException(status_code=404, detail="The region filter option was not found.") from nse
    except WebDriverException as we:
        raise HTTPException(status_code=500, detail="WebDriver encountered an error while selecting the region filter.") from we

    try:
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='Búsqueda avanzada' or @value='Advanced search']"))
        )
        search_button.click()
    except TimeoutException as te:
        raise HTTPException(status_code=504, detail="Timeout occurred while waiting for the 'Advanced Search' button.") from te
    except NoSuchElementException as nse:
        raise HTTPException(status_code=404, detail="The 'Advanced Search' button was not found.") from nse
    except WebDriverException as we:
        raise HTTPException(status_code=500, detail="WebDriver encountered an error while clicking the 'Advanced Search' button.") from we

    try:
        any_date_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'De cualquier fecha') or contains(text(), 'Any time')]"))
        )
        any_date_button.click()
    except TimeoutException as te:
        raise HTTPException(status_code=504, detail="Timeout occurred while waiting for the 'Any time' button.") from te
    except NoSuchElementException as nse:
        raise HTTPException(status_code=404, detail="The 'Any time' button was not found.") from nse
    except WebDriverException as we:
        raise HTTPException(status_code=500, detail="WebDriver encountered an error while clicking the 'Any time' button.") from we

    try:
        customize_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@role='menuitem' and (contains(text(), 'Personalizar...') or contains(text(), 'Custom range...'))]"))
        )
        customize_button.click()
    except TimeoutException as te:
        raise HTTPException(status_code=504, detail="Timeout occurred while waiting for the 'Custom range' button.") from te
    except NoSuchElementException as nse:
        raise HTTPException(status_code=404, detail="The 'Custom range' button was not found.") from nse
    except WebDriverException as we:
        raise HTTPException(status_code=500, detail="WebDriver encountered an error while clicking the 'Custom range' button.") from we

    try:
        start_date, end_date = calculate_dates(date_option)
        start_date_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "OouJcb"))
        )
        end_date_input = driver.find_element(By.ID, "rzG2be")
        start_date_input.send_keys(start_date)
        end_date_input.send_keys(end_date)
    except TimeoutException as te:
        raise HTTPException(status_code=504, detail="Timeout occurred while entering date range.") from te
    except NoSuchElementException as nse:
        raise HTTPException(status_code=404, detail="Date input fields were not found.") from nse
    except WebDriverException as we:
        raise HTTPException(status_code=500, detail="WebDriver encountered an error while entering date range.") from we

    try:
        go_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//g-button[contains(@class, 'Ru1Ao BwGU8e fE5Rge') or contains(@class, 'Ru1Ao BwGU8e fE5Rge')]"))
        )
        go_button.click()
    except TimeoutException as te:
        raise HTTPException(status_code=504, detail="Timeout occurred while waiting for the 'Go' button.") from te
    except NoSuchElementException as nse:
        raise HTTPException(status_code=404, detail="The 'Go' button was not found.") from nse
    except WebDriverException as we:
        raise HTTPException(status_code=500, detail="WebDriver encountered an error while clicking the 'Go' button.") from we

def extract_links(driver):
    all_hrefs = []
    while True:
        check_for_captcha(driver, "Link Extraction - Before Collecting Links")
        div_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.dURPMd"))
        )
        check_for_captcha(driver, "Link Extraction - After Collecting Links")
        
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

def check_for_captcha(driver, phase):
    try:
        captcha_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#captcha, div.g-recaptcha"))
        )
        if captcha_element:
            message = f"CAPTCHA detected during the {phase} phase! Manual intervention required."
            print(message)
            raise HTTPException(status_code=403, detail=message)
    except TimeoutException:
        # No CAPTCHA detected, continue with the operation
        pass

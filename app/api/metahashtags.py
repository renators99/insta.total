# app/api/metahashtags.py
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from datetime import datetime
import time

router = APIRouter()

def init_driver():
    chrome_options = uc.ChromeOptions()
    chrome_prefs = {
        "download.default_directory": os.path.join(os.getcwd(), "data"),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", chrome_prefs)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--headless")
    driver = uc.Chrome(options=chrome_options, use_subprocess=False)
    return driver

@router.get("/search/")
async def run_selenium(search_term: str = Query(..., description="The hashtag or term to search for")):
    download_dir = os.path.join(os.getcwd(), "Data")
    os.makedirs(download_dir, exist_ok=True)
    
    driver = init_driver()
    wait = WebDriverWait(driver, 30)
    
    try:
        url = 'https://metahashtags.com/login'
        driver.get(url)
        
        # Login
        email_input = wait.until(EC.presence_of_element_located((By.ID, "loginEmail")))
        email_input.send_keys("steffan@soixante9.com")
        password_input = wait.until(EC.presence_of_element_located((By.ID, "loginPassword")))
        password_input.send_keys("G7#kP9!mQ2@dX4&z")
        login_button = wait.until(EC.element_to_be_clickable((By.ID, "wp-submit")))
        login_button.click()
        
        # Navigation and search
        related_hashtags_section = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'widget-content-wrapper') and .//h4[text()='Find related hashtags']]")))
        related_hashtags_section.click()
        
        search_input = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "search-input")))
        search_input.send_keys(search_term)
        search_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "search-button")))
        search_button.click()
        
        # 1. Esperar a que el elemento <li> con la clase específica esté presente
        list_item = wait.until(EC.presence_of_element_located((By.XPATH, f"//li[contains(@class, 'list-group-item card hashtag') and .//button[@data-htag='{search_term}']]")))
        
        # 2. Seleccionar el checkbox usando el ID
        checkbox_id = f"checkall-htag-{search_term}"
        checkbox = wait.until(EC.presence_of_element_located((By.ID, checkbox_id)))
        driver.execute_script("arguments[0].click();", checkbox)
        
        # 3. Hacer clic en el botón de exportar
        export_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-exporttags")))
        driver.execute_script("arguments[0].click();", export_button)
        
        # Esperar a que se descargue el archivo
        csv_file_path = os.path.join(download_dir, "MetaHashtags.csv")
        for _ in range(30):  # Esperar hasta 30 segundos
            if os.path.exists(csv_file_path):
                break
            time.sleep(1)
        else:
            raise HTTPException(status_code=404, detail="File download timeout")
        
        # Renombrar el archivo CSV
        current_date = datetime.now().strftime("%Y-%m-%d")
        new_csv_file_path = os.path.join(download_dir, f"{search_term}_{current_date}.csv")
        os.rename(csv_file_path, new_csv_file_path)
        
        driver.quit()
        
        # Devolver el archivo como parte de la respuesta
        return FileResponse(new_csv_file_path, filename=f"{search_term}_{current_date}.csv")
    
    except Exception as e:
        driver.quit()
        raise HTTPException(status_code=500, detail=str(e))


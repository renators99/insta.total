# app/api/metahashtags.py
from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from fastapi.responses import FileResponse
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.utils.selenium_driver import init_driver
import os
from datetime import datetime
import time
import pandas as pd
import zipfile

router = APIRouter()

@router.get("/search-metahashtags/")
async def run_selenium(search_term: str = Query(..., description="The hashtag or term to search for")):
    download_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(download_dir, exist_ok=True)
    
    driver = init_driver()
    wait = WebDriverWait(driver, 60)
    
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
        
        # Devolver la ruta del archivo CSV creado
        return new_csv_file_path
    
    except Exception as e:
        driver.quit()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-metahashtags/")
async def batch_metahashtags(file: UploadFile = File(...)):
    # Crear una carpeta para guardar los resultados en Batch_Data
    batch_download_dir = os.path.join(os.getcwd(), "batch_data")
    os.makedirs(batch_download_dir, exist_ok=True)

    progress_file_path = os.path.join(batch_download_dir, "progress.txt")
    failed_file_path = os.path.join(batch_download_dir, "failed.txt")

    try:
        # Guardar el archivo cargado temporalmente
        temp_file_path = os.path.join(batch_download_dir, file.filename)
        with open(temp_file_path, "wb") as f:
            f.write(file.file.read())
        
        # Leer el archivo XLSX
        df = pd.read_excel(temp_file_path, sheet_name='Sheet1')

        # Verificar si la columna 'Target' existe
        if 'Target' not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column 'Target' not found in XLSX. Available columns: {df.columns.tolist()}")

        # Leer el progreso previo
        start_index = 0
        if os.path.exists(progress_file_path):
            with open(progress_file_path, "r") as f:
                start_index = int(f.read().strip())

        csv_files = []

        # Iterar sobre las filas para obtener los hashtags
        for index in range(start_index, len(df)):
            row = df.iloc[index]
            print(f"Processing row {index + 1}")  # Imprimir el número de la fila que se está procesando
            hashtag = row['Target']
            if pd.notna(hashtag):
                try:
                    csv_file_path = await run_selenium(search_term=hashtag.strip('#'))
                    csv_files.append(csv_file_path)
                except Exception as e:
                    # Registrar el hashtag fallido en el archivo failed.txt
                    with open(failed_file_path, "a") as f:
                        f.write(f"{hashtag}\n")
                    print(f"Failed to process hashtag {hashtag}: {e}")
                    continue
            
            # Guardar el progreso
            with open(progress_file_path, "w") as f:
                f.write(str(index + 1))
        
        # Crear un archivo ZIP con todos los CSV generados
        zip_file_path = os.path.join(batch_download_dir, "MetaHashtags_Batch_" + datetime.now().strftime("%Y-%m-%d") + ".zip")
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for file in csv_files:
                zipf.write(file, os.path.basename(file))

        # Eliminar el archivo de progreso después de completar todo el procesamiento
        if os.path.exists(progress_file_path):
            os.remove(progress_file_path)

        return {"message": f"Batch processing completed successfully. The zip file is located at {zip_file_path}. Failed hashtags are recorded in failed.txt"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Eliminar el archivo temporal
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
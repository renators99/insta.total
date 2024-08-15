import undetected_chromedriver as uc
import os

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
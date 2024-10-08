# app/api/insta_profile_generator.py
from fastapi import APIRouter, HTTPException, Query
from app.utils.selenium_driver import init_driver
from app.utils.search_tools import (
    calculate_dates, 
    search_on_google, 
    apply_filters, 
    extract_result_count, 
    extract_links,
    save_json
)
from app.schemas import SearchResult  # Import the data models
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException

router = APIRouter()

@router.get("/search-google/", response_model=SearchResult)
def google_search_with_tools(search_term: str = Query(...), date_option: int = Query(...)):
    driver = None
    try:
        driver = init_driver()
        search_on_google(driver)
        apply_filters(driver, search_term, date_option)
        result_count = extract_result_count(driver)
        hrefs = extract_links(driver)
        
        start_date, end_date = calculate_dates(date_option)
        results_json = {
            "result_count": result_count,
            "date_range": f"{start_date} - {end_date}",
            "results": hrefs
        }
        
        filename = save_json(results_json, search_term, start_date, end_date)
        
        driver.quit()
        
        return SearchResult(**results_json)
    
    except HTTPException as e:
        if driver:
            driver.quit()
        raise e
    
    except Exception as e:
        if driver:
            driver.quit()
        raise HTTPException(status_code=500, detail=str(e))

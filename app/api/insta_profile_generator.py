# app/api/insta_profile_generator.py
from fastapi import APIRouter, HTTPException, Query
from app.utils.selenium_driver import configure_driver
from app.utils.search_tools import (
    calculate_dates, 
    search_on_google, 
    apply_filters, 
    extract_result_count, 
    extract_links,
    save_json
)
from app.schemas import SearchResult  # Import the data models

router = APIRouter()

@router.get("/search/", response_model=SearchResult)
def google_search_with_tools(search_term: str = Query(...), date_option: str = Query(...)):
    try:
        driver = configure_driver()
        search_on_google(driver, search_term)
        apply_filters(driver, date_option)
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
    
    except Exception as e:
        if driver:
            driver.quit()
        raise HTTPException(status_code=500, detail=str(e))

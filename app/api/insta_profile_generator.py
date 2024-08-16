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
        
        try:
            search_on_google(driver, search_term)
        except TimeoutException as te:
            raise HTTPException(status_code=504, detail="Timeout occurred during Google search initiation.") from te
        except NoSuchElementException as nse:
            raise HTTPException(status_code=404, detail="Required element not found during Google search.") from nse
        except WebDriverException as we:
            raise HTTPException(status_code=500, detail="WebDriver encountered an error during Google search.") from we
        
        try:
            apply_filters(driver, date_option)
        except TimeoutException as te:
            raise HTTPException(status_code=504, detail="Timeout occurred while applying search filters.") from te
        except NoSuchElementException as nse:
            raise HTTPException(status_code=404, detail="Required element not found while applying search filters.") from nse
        except WebDriverException as we:
            raise HTTPException(status_code=500, detail="WebDriver encountered an error while applying search filters.") from we
        
        try:
            result_count = extract_result_count(driver)
        except TimeoutException as te:
            raise HTTPException(status_code=504, detail="Timeout occurred while extracting result count.") from te
        except WebDriverException as we:
            raise HTTPException(status_code=500, detail="WebDriver encountered an error while extracting result count.") from we
        
        try:
            hrefs = extract_links(driver)
        except TimeoutException as te:
            raise HTTPException(status_code=504, detail="Timeout occurred while extracting links.") from te
        except WebDriverException as we:
            raise HTTPException(status_code=500, detail="WebDriver encountered an error while extracting links.") from we

        start_date, end_date = calculate_dates(date_option)
        results_json = {
            "result_count": result_count,
            "date_range": f"{start_date} - {end_date}",
            "results": hrefs
        }
        
        try:
            filename = save_json(results_json, search_term, start_date, end_date)
        except Exception as se:
            raise HTTPException(status_code=500, detail="An error occurred while saving the JSON results.") from se
        
        driver.quit()
        
        return SearchResult(**results_json)
    
    except HTTPException as e:
        if driver:
            driver.quit()
        raise e
    
    except WebDriverException as e:
        if driver:
            driver.quit()
        raise HTTPException(status_code=500, detail="WebDriver encountered an error.") from e
    
    except Exception as e:
        if driver:
            driver.quit()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}") from e
    finally:
        if driver:
            driver.quit()
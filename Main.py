from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import httpx
import os
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dynamic Profile Endpoint Task")


CAT_FACT_URL = "https://catfact.ninja/fact"
API_TIMEOUT = 5.0  

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoint ---

@app.get("/me", response_class=JSONResponse)
async def get_me():
    """
    Returns profile information and a dynamic cat fact.
    """
    
    fallback_cat_fact = "Could not fetch a cat fact at this time. Cats are still awesome!"
    cat_fact = fallback_cat_fact
    
   
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(CAT_FACT_URL)
            
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status() 
            
            fact_data = response.json()
            cat_fact = fact_data.get("fact", fallback_cat_fact)
            
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logger.error(f"Failed to fetch cat fact from external API. Error: {e}")
        # cat_fact remains the default/fallback value
    
    # 2. Generate the dynamic UTC timestamp in ISO 8601 format
    # The 'Z' suffix denotes UTC (Zulu time)
    current_timestamp = (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )
    
    # 3. Assemble the final response payload strictly following the required schema
    response_data = {
        "status": "success", # Must be lowercase "success"
        "user": {
            "email": "okekeebuka225@gmail.com",
            "name": "Ebuka Okeke", 
            "stack": "Python/FastAPI" # Your backend stack as a string
        },
        "timestamp": current_timestamp,
        "fact": cat_fact
    }
    
    # 4. Return the JSON response with the HTTP 200 OK status
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)
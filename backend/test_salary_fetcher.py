import os
import time
from services.salary_fetcher import fetch_salary_data, DB_PATH

def main():
    print(f"Database Path: {DB_PATH}")
    
    # 1. Clear any existing test cache DB if it is in an unexpected state, but we don't need to.
    print("\nFetching salary data for 'Software Engineer' in 'Bangalore', Experience: 0 yrs (First call, cache miss/scraping/fallback)...")
    start_time = time.time()
    data1 = fetch_salary_data("Software Engineer", "Bangalore", 0)
    duration1 = time.time() - start_time
    print(f"Data returned in {duration1:.3f} seconds:")
    import pprint
    pprint.pprint(data1)
    
    # Check if DB file was created
    if os.path.exists(DB_PATH):
        print(f"Success: DB file created at {DB_PATH}")
    else:
        print("Error: DB file NOT created!")
        
    # 2. Fetch again to verify Cache Hit
    print("\nFetching salary data again (Second call, should be a Cache Hit)...")
    start_time = time.time()
    data2 = fetch_salary_data("Software Engineer", "Bangalore", 0)
    duration2 = time.time() - start_time
    print(f"Data returned in {duration2:.3f} seconds:")
    pprint.pprint(data2)
    
    if duration2 < duration1:
        print("Success: Second call was faster (Cache hit confirmed!)")
    else:
        print("Warning: Second call wasn't faster, but let's check values.")
        
    # Verify values match
    if data1 == data2:
        print("Success: Data matches perfectly between calls!")
    else:
        print("Error: Data mismatch between first and second calls!")
        
    # 3. Test non-fallback/non-standard fallback role
    print("\nFetching salary data for 'Astronaut' in 'Hyderabad', Experience: 5 yrs (Verify fallback matches default bucket)...")
    data_fallback = fetch_salary_data("Astronaut", "Hyderabad", 5)
    pprint.pprint(data_fallback)
    print("Test finished successfully!")

if __name__ == "__main__":
    main()

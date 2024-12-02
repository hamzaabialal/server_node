import geonamescache
import threading
import subprocess

# List of famous countries (ISO Alpha-2 country codes)
famous_country_codes = ['US', 'GB', 'CA', 'AU', 'IN']  # Add/remove country codes as needed

# Get country names from geonamescache
gc = geonamescache.GeonamesCache()
countries = gc.get_countries()
famous_countries = {code: countries[f"ISO_ALPHA2:{code}"]['name'] for code in famous_country_codes}

# Function to execute the command
def run_scraper(niche, city, country):
    command = f"python scraper_node.py --niche \"{niche}\" --city \"{city}\" --country \"{country}\""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"Command executed for city {city} in {country}:\n{result.stdout}")
        if result.stderr:
            print(f"Error for city {city} in {country}:\n{result.stderr}")
    except Exception as e:
        print(f"Error executing command for city {city} in {country}: {e}")

# Function to get cities for a country
def get_cities(country_code):
    cities = gc.get_cities()
    city_names = []
    for _, city_info in cities.items():
        if city_info['countrycode'] == country_code:
            city_names.append(city_info['name'])
    return city_names  # No limit

# Main function
def main():
    niche = "Shoes"  # Replace with your desired niche
    threads = []
    for country_code, country_name in famous_countries.items():
        cities = get_cities(country_code)
        for city in cities:
            if len(threads) < 5:  # Limit to 5 concurrent threads
                thread = threading.Thread(target=run_scraper, args=(niche, city, country_name))
                threads.append(thread)
                thread.start()
            else:
                # Wait for one thread to finish before starting a new one
                for t in threads:
                    t.join()
                threads = []
    
    # Join any remaining threads
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()

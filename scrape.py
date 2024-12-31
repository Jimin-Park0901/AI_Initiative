import time
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from googlesearch import search
import pandas as pd

def scrape_website(website):
    print("Launching chrome browser...")

    chrome_driver_path = "./chromedriver"
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)

    try:
        driver.get(website)
        print("Page loaded...")
        html = driver.page_source
        return html
    except Exception as e:
        print(f"Error loading page: {e}")
        return ""
    finally:
        driver.quit()  # Ensure driver is properly closed

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")

    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Get text or further process the content
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content

def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
    ]

def search_and_scrape_model_details(model_names, domain):
    """
    Search for each model name and extract data from the first result.
    """
    detailed_data = []

    for model_name in model_names:
        query = f"{model_name} site:{domain}"
        print(f"Searching for: {query}")

        try:
            search_results = list(search(query, num_results=1, pause=2))

            if search_results:
                detailed_url = search_results[0]
                print(f"Scraping URL: {detailed_url}")

                # Scrape the detailed page
                html = scrape_website(detailed_url)
                cleaned_content = clean_body_content(html)
                detailed_data.append({
                    "Model Name": model_name,
                    "URL": detailed_url,
                    "Content": cleaned_content
                })
            else:
                print(f"No results found for {model_name}")
                detailed_data.append({
                    "Model Name": model_name,
                    "URL": "No results",
                    "Content": ""
                })

        except Exception as e:
            print(f"Error during search and scrape for {model_name}: {e}")
            detailed_data.append({
                "Model Name": model_name,
                "URL": "Error",
                "Content": str(e)
            })

        # To avoid getting blocked by search engines
        time.sleep(2)

    return detailed_data

def save_to_excel(data, file_name):
    """
    Save the extracted data to an Excel file.
    """
    df = pd.DataFrame(data)
    df.to_excel(file_name, index=False)
    print(f"Data saved to {file_name}")

# Example usage
if __name__ == "__main__":
    # Example model names and domain
    models = ["Model1", "Model2", "Model3"]
    user_domain = "example.com"

    # Step 1: Search and scrape detailed information for each model
    detailed_info = search_and_scrape_model_details(models, user_domain)

    # Step 2: Save results to an Excel file
    save_to_excel(detailed_info, "detailed_model_info.xlsx")

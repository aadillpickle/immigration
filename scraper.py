import requests
from bs4 import BeautifulSoup

def fetch_and_save_paragraphs(url, filename):
    try:
        # Fetching the webpage content
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')

        # Writing paragraphs to file and displaying the progress
        with open(filename, 'w', encoding='utf-8') as file:
            total_paragraphs = len(paragraphs)
            for index, paragraph in enumerate(paragraphs):
                file.write(paragraph.text + '\n')
                progress_percentage = ((index + 1) / total_paragraphs) * 100
                print(f"Progress: {progress_percentage:.2f}%", end='\r')

            print()  # Print a newline character to move the cursor to the next line after progress completion

        print(f"Paragraphs from {url} have been saved to {filename}")
    except requests.HTTPError as e:
        print(f"Unable to fetch data from {url}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Replace with the actual URL you want to scrape
url = "https://www.uscis.gov/book/export/html/68600"
fetch_and_save_paragraphs(url, "data.txt")

import requests

class WebAgent:
    def __init__(self):
        self.session = requests.Session()

    def process_request(self, prompt: str):
        # Process the web-related request
        print(f"WebAgent processing request: {prompt}")
        return "WebAgent response"

    def scrape_website(self, url: str):
        try:
            response = self.session.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.text
        except requests.exceptions.RequestException as e:
            return f"Error scraping {url}: {e}"

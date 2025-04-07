from bs4 import BeautifulSoup
import requests
from requests import Response

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 "
                  "Safari/537.36"
}


class Website:
    """
    A utility class to represent a Website that we have scraped, now with links.
    This class is enhanced from https://github.com/ed-donner/llm_engineering
    """
    def __init__(self, url: str):
        self.url = url
        self.title: str
        self.text: str
        self.links: []

        try:
            response = requests.get(url, headers=headers)
            self.__parse_website(response)
        except Exception as e:
            self.title = ""
            self.text = ""
            self.links = []

    def __parse_website(self, response: Response):
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""
        links = [link.get('href') for link in soup.find_all('a')]
        self.links = [link for link in links if link]

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"

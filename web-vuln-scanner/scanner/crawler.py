from .utils import send_request, extract_forms, extract_links
from urllib.parse import urlparse

class Crawler:
    def __init__(self, start_url, max_pages=10):
        self.start_url = start_url
        self.max_pages = max_pages
        self.visited = set()
        self.to_visit = [start_url]
        self.forms = []
        self.links = []
        self.base_domain = urlparse(start_url).netloc

    def crawl(self):
        while self.to_visit and len(self.visited) < self.max_pages:
            url = self.to_visit.pop(0)
            if url in self.visited:
                continue
            print(f"Crawling: {url}")
            response = send_request(url)
            if response and response.status_code == 200:
                self.visited.add(url)
                forms = extract_forms(response.text, url)
                self.forms.extend(forms)
                links = extract_links(response.text, url)
                for link in links:
                    if link not in self.visited and link not in self.to_visit:
                        self.to_visit.append(link)
            else:
                self.visited.add(url)
                print(f"Failed to crawl {url}")
        return self.forms, list(self.visited)
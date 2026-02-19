import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

TIMEOUT = 10

def send_request(url, method='GET', data=None, cookies=None):
    try:
        if method.upper() == 'GET':
            return requests.get(url, params=data, cookies=cookies, timeout=TIMEOUT)
        elif method.upper() == 'POST':
            return requests.post(url, data=data, cookies=cookies, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        print(f"Timeout: {url}")
    except requests.exceptions.ConnectionError:
        print(f"Connection error: {url}")
    except Exception as e:
        print(f"Request failed: {url} - {e}")
    return None

def extract_forms(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    forms = []
    for form in soup.find_all('form'):
        action = form.get('action')
        method = form.get('method', 'get').lower()
        inputs = []
        for inp in form.find_all('input'):
            name = inp.get('name')
            inp_type = inp.get('type', 'text')
            if name:
                inputs.append({'name': name, 'type': inp_type})
        if action:
            if action.startswith('http'):
                form_url = action
            else:
                form_url = urljoin(base_url, action)
        else:
            form_url = base_url
        forms.append({'url': form_url, 'method': method, 'inputs': inputs})
    return forms

def extract_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    base_domain = urlparse(base_url).netloc
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        if parsed.netloc == base_domain or parsed.netloc.endswith('.' + base_domain):
            links.add(full_url)
    return list(links)
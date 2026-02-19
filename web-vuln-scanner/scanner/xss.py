from .utils import send_request

XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert(1)>",
    "\"><script>alert(1)</script>",
    "javascript:alert('XSS')"
]

def test_xss(url, form_details):
    vulns = []
    for payload in XSS_PAYLOADS:
        data = {}
        for inp in form_details['inputs']:
            if inp['type'] != 'submit':
                data[inp['name']] = payload
        if form_details['method'] == 'post':
            response = send_request(form_details['url'], method='POST', data=data)
        else:
            response = send_request(form_details['url'], method='GET', data=data)
        if response and payload in response.text:
            vulns.append({
                'payload': payload,
                'url': form_details['url'],
                'method': form_details['method'],
                'parameter': list(data.keys())[0] if data else 'unknown'
            })
            break
    return vulns
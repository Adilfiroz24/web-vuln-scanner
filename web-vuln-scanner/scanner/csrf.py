def test_csrf(form_details):
    for inp in form_details['inputs']:
        if inp['type'] == 'hidden' and ('csrf' in inp['name'].lower() or 'token' in inp['name'].lower()):
            return []
    if form_details['method'] == 'post':
        return [{
            'url': form_details['url'],
            'method': form_details['method'],
            'issue': 'No CSRF token found in POST form'
        }]
    return []
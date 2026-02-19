import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, request, Response, stream_with_context, jsonify
import json
import traceback
import time

from scanner.crawler import Crawler
from scanner.xss import test_xss
from scanner.sqli import test_sqli
from scanner.csrf import test_csrf

app = Flask(__name__)

def scan_generator(target_url, max_pages):
   
    def send(data):
        return f"data: {json.dumps(data)}\n\n"

    last_heartbeat = time.time()
    def maybe_heartbeat():
        nonlocal last_heartbeat
        if time.time() - last_heartbeat > 5:
            yield ': heartbeat\n\n'          # comment line (correct format)
            last_heartbeat = time.time()

    yield send({'type': 'status', 'message': f'Scan started for {target_url}'})

    try:
        yield send({'type': 'status', 'message': 'Crawling website...'})
        crawler = Crawler(target_url, max_pages)
        forms, crawled_urls = crawler.crawl()
        yield send({'type': 'status', 'message': f'Crawled {len(crawled_urls)} pages, found {len(forms)} forms.'})

        vulnerabilities = []

        for idx, form in enumerate(forms, 1):
            yield from maybe_heartbeat()
            yield send({'type': 'status', 'message': f'Testing form {idx}/{len(forms)} at {form["url"]}'})

            # XSS
            for v in test_xss(form['url'], form):
                v.update({'type': 'XSS', 'severity': 'High', 'owasp': 'A7: Cross-Site Scripting'})
                vulnerabilities.append(v)
                yield send({'type': 'vuln', 'vulnerability': v})

            # SQLi
            for v in test_sqli(form['url'], form):
                v.update({'type': 'SQL Injection', 'severity': 'Critical', 'owasp': 'A1: Injection'})
                vulnerabilities.append(v)
                yield send({'type': 'vuln', 'vulnerability': v})

            # CSRF
            for v in test_csrf(form):
                v.update({'type': 'CSRF', 'severity': 'Medium', 'owasp': 'A8: Cross-Site Request Forgery'})
                vulnerabilities.append(v)
                yield send({'type': 'vuln', 'vulnerability': v})

        summary = {
            'target': target_url,
            'crawled_urls': list(crawled_urls),
            'vulnerabilities': vulnerabilities
        }
        yield send({'type': 'complete', 'summary': summary})

        with open('results.json', 'w') as f:
            json.dump(summary, f, indent=4)

    except Exception as e:
        traceback.print_exc()
        yield send({'type': 'error', 'message': str(e)})


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/scan/stream')
def scan_stream():
    target_url = request.args.get('url', '').strip()
    max_pages = request.args.get('max_pages', 10)

    if not target_url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        max_pages = int(max_pages)
    except ValueError:
        max_pages = 10

    print(f"Stream started for {target_url} (max {max_pages})")
    return Response(
        scan_generator(target_url, max_pages),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
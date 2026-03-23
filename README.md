1️⃣ Web Vulnerability Scanner
# Web Application Vulnerability Scanner

## Description

This project is a Python-based Web Application Vulnerability Scanner that detects common web security issues such as Cross-Site Scripting (XSS) and SQL Injection (SQLi). The scanner crawls web pages, finds input fields, injects test payloads, and analyzes server responses to identify vulnerabilities.

## Features

* Website crawling
* Detection of XSS vulnerabilities
* Detection of SQL Injection
* Scan result reporting
* Simple web interface using Flask

## Technologies Used

* Python
* Flask
* Requests
* BeautifulSoup

## How to Run

1. Install dependencies:

```
pip install -r requirements.txt
```

2. Run the scanner:

```
python app.py
```

3. Open the browser and go to:

```
http://127.0.0.1:5000
```

## Purpose

The goal of this project is to demonstrate how automated tools can identify common web application vulnerabilities.

## Disclaimer

This tool is created for educational purposes only. Do not use it against systems without permission.

2️⃣ Network Intrusion Detection System (NIDS)
# Network Intrusion Detection System (NIDS)

## Description

This project is a Python-based Network Intrusion Detection System that monitors network traffic and detects suspicious activities based on predefined signature rules.

## Features

* Network packet capture
* Signature-based intrusion detection
* Suspicious traffic alerts
* Packet analysis
* Docker support for deployment

## Technologies Used

* Python
* Scapy
* Docker
* JSON rule engine

## How to Run

Install dependencies:

```
pip install -r requirements.txt
```

Run the detection system:

```
python main.py
```

For Docker deployment:

```
docker-compose up
```

## Purpose

The objective of this project is to simulate a basic intrusion detection system similar to tools like Snort or Suricata.

## Disclaimer

This project is intended for educational and research purposes only.

3️⃣ Linux Hardening Audit Tool
# Linux Hardening Audit Tool

## Description

The Linux Hardening Audit Tool analyzes a Linux system to detect security misconfigurations and weak security settings. It checks firewall status, SSH configurations, and sensitive file permissions.

## Features

* Firewall configuration check
* SSH security audit
* File permission verification
* Security scoring system
* Audit report generation

## Technologies Used

* Python
* Linux system commands
* OS and subprocess modules

## How to Run

Run the script using:

```
python audit.py
```

Some checks may require sudo privileges.

## Purpose

This tool helps identify security weaknesses in Linux systems and suggests hardening improvements.

## Disclaimer

This tool is developed for learning and security auditing purposes only.

4️⃣ Log File Analyzer for Intrusion Detection
# Log File Analyzer for Intrusion Detection

## Description

This project analyzes server log files to detect suspicious activities such as brute-force attacks, repeated login failures, and abnormal access patterns.

## Features

* SSH log analysis
* Apache log analysis
* Brute force detection
* Suspicious IP identification
* Incident report generation

## Technologies Used

* Python
* Regex
* Log parsing techniques

## How to Run

Run the analyzer:

```
python analyzer.py
```

The generated report will be saved in the reports folder.

## Purpose

The goal of this project is to demonstrate how log analysis can be used to detect potential security threats.

## Disclaimer

This project is intended for educational use in cybersecurity training.

5️⃣ Cyber Threat Intelligence Dashboard
# Cyber Threat Intelligence Dashboard

## Description

This project is a dashboard that collects and displays threat intelligence data from public security APIs such as VirusTotal and AbuseIPDB. It allows users to check the reputation of IP addresses and identify malicious indicators.

## Features

* IP reputation lookup
* Integration with threat intelligence APIs
* Threat score visualization
* Search history storage
* Web dashboard interface

## Technologies Used

* Python
* Flask
* VirusTotal API
* AbuseIPDB API
* Chart.js

## How to Run

Install dependencies:

```
pip install -r requirements.txt
```

Start the application:

```
python app.py
```

Open in browser:

```
http://127.0.0.1:5000
```

## Purpose

The dashboard helps visualize and analyze threat intelligence data for security investigation.

## Disclaimer

This tool is developed for educational purposes and cybersecurity research.

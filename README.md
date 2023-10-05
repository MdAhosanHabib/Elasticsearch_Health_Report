# ELK Health Check Script

<img width="455" alt="ELK Report" src="https://github.com/MdAhosanHabib/Elasticsearch_Health_Report/assets/43145662/07dfa5d6-5796-4ccf-b177-e60658bb6048">

## Overview
The ELK Health Check Script is a Python script designed to monitor the health and status of an Elasticsearch-Logstash-Kibana (ELK) stack. The script provides essential information about Elasticsearch snapshots, ELK version, cluster health, and server disk usage. It also includes an email alert feature to notify administrators of any snapshot failures.

This theory document provides an overview of the script's purpose, features, usage, and architecture.


## Purpose
The primary purpose of the ELK Health Check Script is to:

Monitor the status of Elasticsearch snapshots and provide a report.

Retrieve information about the ELK stack, including version and cluster name.

Monitor server disk usage and display it in an HTML report.

Send email alerts when Elasticsearch snapshots fail.

## Features
1. Elasticsearch Snapshot Monitoring

2. ELK Stack Information

3. Server Disk Usage Monitoring

4. Email Alerts, Sends email alerts when Elasticsearch snapshots fail. Administrators can configure the sender and recipient email addresses, SMTP server, and port.


## Dependencies

Python 3.6

requests

bs4 (Beautiful Soup)

smtplib (for email alerts)

## Configuration
The script includes configuration variables at the beginning of the file. Administrators should adjust these variables according to their specific environment and requirements.

After Successful deployment we can get like this:

![elasticsearch_backup_report](https://github.com/MdAhosanHabib/Elasticsearch_Health_Report/assets/43145662/d7c23f1b-a8c5-4549-899d-968f786e532a)

Thanks from Ahosan Habib

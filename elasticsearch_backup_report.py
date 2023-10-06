#############################################################################
# Purpose : The purpose of this script is to report ELK health check        #
# Name                   Date                                Version        #
# **************************************************************************#
# ELK Health Script    4-10-23                               1.0            #
# By Ahosan Habib(DBA_DevOps)                                               #
#############################################################################

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ELASTICSEARCH_HOST = "10.0.10.10"
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_REPO = "my_elk_backup"

sender_email = "notify@bd.com"
receiver_email = "data@bd.com"
smtp_server = "10.0.11.11"
smtp_port = 55

#get Elasticsearch snapshot information
def get_snapshot_info():
    url = f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}/_snapshot/{ELASTICSEARCH_REPO}/_all"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            print("Error: Response is not valid JSON")
            print("Response Content:")
            print(response.content)
            return None
    else:
        print(f"Error: Failed to retrieve data. Status code: {response.status_code}")
        return None

#run shell command and capture output
def run_shell_command(command):
    try:
        result = subprocess.check_output(command, shell=True, universal_newlines=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return None

#ELK version and cluster name from Elasticsearch
def get_elk_info():
    url = f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}/"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            elk_version = data['version']['number']
            elk_cluster_name = data['cluster_name']
            return elk_version, elk_cluster_name
        except (KeyError, ValueError):
            print("Error: Failed to retrieve ELK information from Elasticsearch response.")
            return None, None
    else:
        print(f"Error: Failed to retrieve ELK information. Status code: {response.status_code}")
        return None, None

#get mount point usage including total size, free size, and usage in GB
def get_mount_point_usage():
    df_output = run_shell_command("df -h --output=target,size,avail,pcent | awk 'NR>1 {print $1, $2, $3, $4}'")
    if df_output:
        return df_output.split('\n')
    else:
        return []

def convert_size_to_gb(size_str):
    size_str = size_str.strip()
    if size_str.endswith('G'):
        return size_str[:-1]
    elif size_str.endswith('T'):
        return str(float(size_str[:-1]) * 1024)
    elif size_str.endswith('M'):
        return str(float(size_str[:-1]) / 1024)
    elif size_str.endswith('K'):
        return str(float(size_str[:-1]) / (1024 * 1024))
    else:
        return None

#send an email alert if failed snapshot
def send_email_alert(snapshot_name, error_message):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"ELK Snapshot Failed: {snapshot_name}"

    body = f"Snapshot '{snapshot_name}' failed with the following error:\n\n{error_message}"
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print(f"Email alert sent for snapshot '{snapshot_name}' failure.")
    except Exception as e:
        print(f"Error sending email alert: {str(e)}")

#create an HTML report
def create_html_report(snapshot_info, elk_version, elk_cluster_name, mount_point_usage):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hostname = run_shell_command("hostname")
    ip_address = run_shell_command("hostname -I | cut -d' ' -f1")

    report = f"""
        <html>
        <head>
            <title>ELK Snapshot Report</title>
            <style>
                body {{
                    text-align: center;
                }}
                table {{
                    margin: 0 auto;
                }}
            </style>
        </head>
        <body>
            <h1>Elasticsearch Snapshot Report</h1>
            <p>Generated at: {current_datetime}</p>
            <p>Hostname: {hostname}</p>
            <p>IP Address: {ip_address}</p>
            <p>ELK Version: {elk_version}</p>
            <p>ELK Cluster Name: {elk_cluster_name}</p>
            <table border='1'>
                <tr>
                    <th>Snapshot Name</th>
                    <th>Status</th>
                    <th>Shards</th>
                    <th>Success</th>
                    <th>Failed</th>
                    <th>Start Time</th>
                    <th>End Time</th>
                </tr>
    """

    for snapshot_data in snapshot_info['snapshots']:
        snapshot_name = snapshot_data['snapshot']
        status = snapshot_data['state']
        start_time = snapshot_data['start_time']
        end_time = snapshot_data['end_time']
        #get elk shards info
        shards_get = snapshot_data['shards']
        total_shards = shards_get['total']
        shards_success = shards_get['successful']
        shards_failed = shards_get['failed']

        if status == "SUCCESS":
            status_html = f"<font color='green'>{status}</font>"
        elif status == "FAILED":
            status_html = f"<font color='red'>{status}</font>"
            #send_email_alert(snapshot_name, "Snapshot failed. Check the Elasticsearch logs for details.")
        else:
            status_html = status
        report += f"<tr><td>{snapshot_name}</td><td>{status_html}</td><td>{total_shards}</td><td>{shards_success}</td><td>{shards_failed}</td><td>{start_time}</td><td>{end_time}</td></tr>"

    report += """
            </table>
            <p>Mount Point Usage:</p>
            <table border='1'>
                <tr>
                    <th>Mount Point</th>
                    <th>Total Size (GB)</th>
                    <th>Free Size (GB)</th>
                    <th>Usage (%)</th>
                </tr>
    """
    for mount_point in mount_point_usage:
        if mount_point:
            mount_info = mount_point.split()
            if len(mount_info) == 4:
                mount, total_size, free_size, usage = mount_info
                total_size_gb = convert_size_to_gb(total_size)
                free_size_gb = convert_size_to_gb(free_size)
                if total_size_gb is not None and free_size_gb is not None:
                    report += f"<tr><td>{mount}</td><td>{total_size_gb}</td><td>{free_size_gb}</td><td>{usage}</td></tr>"

    report += """
            </table>
        </body>
        </html>
    """
    return report

if __name__ == "__main__":
    snapshot_info = get_snapshot_info()
    elk_version, elk_cluster_name = get_elk_info()
    mount_point_usage = get_mount_point_usage()

    if snapshot_info and elk_version and elk_cluster_name:
        html_report = create_html_report(snapshot_info, elk_version, elk_cluster_name, mount_point_usage)
        with open("/db_backup/scripts/elasticsearch_backup_report.html", "w") as file:
            file.write(html_report)
        print("HTML report created successfully.")
    else:
        print("Failed to retrieve necessary information from Elasticsearch.")

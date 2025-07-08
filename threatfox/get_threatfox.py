#!/usr/bin/env python3
import requests
import urllib3
import json
import sys
import csv
import pandas as pd
from tqdm import tqdm
from datetime import date
from urllib.parse import urlparse
import argparse
import os   # Added for environment variable handling

def get_week_number():
    return date.today().isocalendar()[1]

def clean_ioc(ioc):
    # Check if ioc is a URL
    if ioc.startswith('http://') or ioc.startswith('https://'):
        netloc = urlparse(ioc).netloc
        # Check if the domain includes a port
        if ':' in netloc:
            return netloc.split(':')[0]
        else:
            return netloc
    # Check if ioc is an IP address with a port
    elif ':' in ioc:
        return ioc.split(':')[0]
    else:
        return ioc

def is_ip(ioc):
    parts = ioc.split('.')
    return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

def is_domain(ioc):
    return not is_ip(ioc) and '.' in ioc

# Parse command-line arguments
parser = argparse.ArgumentParser(description='ThreatFox IOC Fetcher')
parser.add_argument('days', type=int, help='Number of days to fetch IOCs for')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
args = parser.parse_args()

# Enable verbose output if -v is specified
verbose = args.verbose

def log(message):
    if verbose:
        print(message)

log("Starting script...")

pool = urllib3.HTTPSConnectionPool('threatfox-api.abuse.ch', port=443, maxsize=50)

data = {
    'query':    'get_iocs',
    'days':     args.days
}

log(f"Fetching IOCs for the past {args.days} days...")

# === API KEY SECTION (Environment Variable) ===
auth_key = os.environ.get('THREATFOX_API_KEY')
if not auth_key:
    print("\nError: ThreatFox API key not found.\n")
    print("Please set your API key as an environment variable like this:\n")
    print("    export THREATFOX_API_KEY='your_actual_key_here'\n")
    sys.exit(1)

headers = {
    'Content-Type': 'application/json',
    'Auth-Key': auth_key
}
response = pool.request("POST", "/api/v1/", body=json.dumps(data), headers=headers)
response = response.data.decode("utf-8", "ignore")

week_number = get_week_number()
json_filename = f'wk{week_number}.json'
with open(json_filename, 'w') as json_file:
    json_file.write(response)

with open(json_filename, 'r') as json_file:
    data = json.load(json_file)

# Check if 'data' key exists in the response
if 'data' not in data or not data['data']:
    print("No data found in the API response.")
    quit()

# Convert the data to a pandas DataFrame
try:
    df = pd.DataFrame(data['data'])
except ValueError as e:
    print(f"Error creating DataFrame: {e} Pick a number between 1 and 7 days.")
    quit()

# Clean the 'ioc' column
df['ioc'] = df['ioc'].apply(clean_ioc)

# Convert the DataFrame back to a list of dictionaries
data['data'] = df.to_dict('records')

csv_filename = f'wk{week_number}.csv'
with open(csv_filename, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    if 'data' in data and data['data']:
        # Write the keys from the first item as column headers
        writer.writerow(data['data'][0].keys())
        for item in tqdm(data['data']):
            if isinstance(item, dict):
                row = [str(value).strip() for value in item.values()]
                writer.writerow(row)
            else:
                print(f"Unexpected item: {item}")

# Create separate DataFrames for IPs and domains
ip_df = df[df['ioc'].apply(is_ip)]
domain_df = df[df['ioc'].apply(is_domain)]

# Write IPs to a CSV file
ip_csv_filename = f'wk{week_number}_ip.csv'
ip_df[['ioc']].to_csv(ip_csv_filename, index=False, header=['ip'])

# Write domains to a CSV file
domain_csv_filename = f'wk{week_number}_domain.csv'
domain_df[['ioc']].to_csv(domain_csv_filename, index=False, header=['domain'])
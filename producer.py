import os
import boto3
import requests
import json
from datetime import datetime

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "your-api-key-here")
QUEUE_URL = os.environ.get("QUEUE_URL", "your-queue-url-here")

sqs = boto3.client('sqs', region_name='us-east-1')

def fetch_jobs():
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }
    params = {
        "query": "data engineer in United States",
        "num_pages": "1",
        "date_posted": "today"
    }
    response = requests.get(url, headers=headers, params=params)
    print(f"API Status: {response.status_code}")
    data = response.json()
    return data.get("data", [])

def send_to_sqs(job):
    message = {
        "job_id": job.get("job_id"),
        "job_title": job.get("job_title"),
        "employer_name": job.get("employer_name"),
        "job_city": job.get("job_city"),
        "job_state": job.get("job_state"),
        "job_country": job.get("job_country"),
        "job_description": job.get("job_description", "")[:500],
        "job_posted_at": job.get("job_posted_at_datetime_utc"),
        "job_min_salary": job.get("job_min_salary"),
        "job_max_salary": job.get("job_max_salary"),
        "job_url": job.get("job_apply_link") or job.get("job_google_link", "N/A"),
        "ingested_at": datetime.utcnow().isoformat()
    }
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(message)
    )
    print(f"✅ Sent: {message['job_title']} @ {message['employer_name']} | {message['job_url']}")

def main():
    print("🔍 Fetching jobs...")
    jobs = fetch_jobs()
    if not jobs:
        print("⚠️ No jobs returned. Check your API key.")
        return
    print(f"📦 Found {len(jobs)} jobs. Sending to SQS...")
    for job in jobs:
        send_to_sqs(job)
    print("🎉 Done!")

main()
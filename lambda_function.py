import json
import boto3
from datetime import datetime

s3 = boto3.client('s3')
BUCKET_NAME = 'job-postings-raw-husna'

def lambda_handler(event, context):
    print(f"Received {len(event['Records'])} messages")
    
    for record in event['Records']:
        body = json.loads(record['body'])
        
        job_id = body.get('job_id', 'unknown')
        job_title = body.get('job_title', 'unknown')
        employer = body.get('employer_name', 'unknown')
        
        today = datetime.utcnow().strftime('%Y/%m/%d')
        s3_key = f"jobs/{today}/{job_id}.json"
        
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=json.dumps(body),
            ContentType='application/json'
        )
        
        print(f"Saved: {job_title} @ {employer} -> {s3_key}")
    
    return {'statusCode': 200}

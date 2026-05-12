# Real-Time Job Market Intelligence Pipeline

A fully automated data pipeline that streams live job postings into AWS and displays them in an interactive dashboard.

## Architecture

```mermaid
cd ~/Desktop/job-pipeline
cat > README.md << 'EOF'
# Real-Time Job Market Intelligence Pipeline

A fully automated data pipeline that streams live job postings into AWS and displays them in an interactive dashboard.

## Architecture

```mermaid
flowchart LR
    A[EventBridge\n10 AM daily] -->|trigger| B[Producer Lambda]
    B -->|fetch| C[JSearch API]
    B -->|stream| D[SQS Queue]
    D -->|trigger| E[Consumer Lambda]
    E -->|save| F[Amazon S3]
    F -->|catalog| G[AWS Glue]
    G -->|query| H[Athena]
    F -->|read| I[Streamlit Dashboard]
```

## Tech Stack
- Python, boto3, Streamlit
- AWS EventBridge, Lambda, SQS, S3, Glue, Athena
- JSearch API (RapidAPI)

## How it works
1. EventBridge triggers the producer Lambda every day at 10 AM EST
2. Producer fetches live data engineering job postings from JSearch API
3. Each posting is sent as a message to an AWS SQS queue
4. Consumer Lambda automatically triggers on new SQS messages
5. Job data is stored in S3 as JSON, partitioned by date
6. Glue Crawler catalogs the data for Athena SQL queries
7. Streamlit dashboard reads from S3 and displays jobs with Apply links

## Dashboard features
- Filter jobs by state
- Search by title or company
- View salary ranges
- Direct Apply links to job postings

## Setup
1. Clone the repo
2. Install dependencies: pip install boto3 requests streamlit pandas
3. Configure AWS CLI: aws configure
4. Set environment variables: RAPIDAPI_KEY and QUEUE_URL
5. Run dashboard: streamlit run dashboard.py

import streamlit as st
import boto3
import json
import pandas as pd
import os

BUCKET_NAME = "job-postings-raw-husna"
s3 = boto3.client(
    's3',
    region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'),
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)

def load_jobs():
    jobs = []
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=BUCKET_NAME, Prefix='jobs/')
    all_objects = []
    for page in pages:
        all_objects.extend(page.get('Contents', []))
    all_objects = sorted(all_objects, key=lambda x: x['LastModified'], reverse=True)[:50]
    for obj in all_objects:
        try:
            response = s3.get_object(Bucket=BUCKET_NAME, Key=obj['Key'])
            job = json.loads(response['Body'].read().decode('utf-8'))
            jobs.append(job)
        except:
            pass
    return pd.DataFrame(jobs) if jobs else pd.DataFrame()

st.set_page_config(page_title="Job Market Intelligence", page_icon="💼", layout="wide")
st.title("💼 Real-Time Job Market Intelligence")
st.caption("Powered by AWS S3 + Lambda + SQS")

with st.spinner("Loading jobs from S3..."):
    df = load_jobs()

if df.empty:
    st.warning("No jobs found.")
else:
    col1, col2 = st.columns(2)
    with col1:
        states = ["All"] + sorted(df['job_state'].dropna().unique().tolist())
        selected_state = st.selectbox("Filter by State", states)
    with col2:
        search = st.text_input("Search by title or company", "")
    filtered = df.copy()
    if selected_state != "All":
        filtered = filtered[filtered['job_state'] == selected_state]
    if search:
        mask = (filtered['job_title'].str.contains(search, case=False, na=False) | filtered['employer_name'].str.contains(search, case=False, na=False))
        filtered = filtered[mask]
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Jobs", len(filtered))
    col2.metric("Companies", filtered['employer_name'].nunique())
    col3.metric("States", filtered['job_state'].nunique())
    st.divider()
    st.subheader(f"Showing {len(filtered)} jobs")
    for _, job in filtered.iterrows():
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {job.get('job_title', 'N/A')}")
                st.markdown(f"**{job.get('employer_name', 'N/A')}** — {job.get('job_city', '')} {job.get('job_state', '')}")
                try:
                    salary_min = job.get('job_min_salary')
                    salary_max = job.get('job_max_salary')
                    if salary_min and salary_max and str(salary_min) != 'nan':
                        st.markdown(f"💰 ${int(float(salary_min)):,} — ${int(float(salary_max)):,}")
                except:
                    pass
            with col2:
                try:
                    url = job.get('job_url', 'N/A')
                    if url and url != 'N/A' and isinstance(url, str):
                        st.link_button("Apply →", url)
                except:
                    pass
            st.divider()
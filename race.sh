#!/bin/bash

set -e

# Set the counter to 0 and the files to be used
counter=0
files="data1.json,data2.json,data3.json"

# Function to send POST request
send_post_request() {
    file=$(echo $files | tr "," "\n" | sort --random-sort | head -n 1)
    data='{"data": "'"$counter"'"}'
    result=$(curl -s -X POST -d "$data" -H 'Content-Type: application/json' localhost:8080/write/$file)
    echo "[$(date +%s)] post request result: $result"
}

# Function to send GET request
send_get_request() {
    file=$(echo $files | tr "," "\n" | sort --random-sort | head -n 1)
    result=$(curl -s localhost:8080/read/$file)
    echo "[$(date +%s)] get request result: $result"
}

# Array to store the background job IDs
job_ids=()

while [ $counter -lt 500 ]; do
    # Run the requests concurrently and store the job IDs
    (
        send_post_request &
        send_get_request &
    ) &
    job_ids+=($!)

    # Increment the counter
    ((counter++))
done

# Wait for all background jobs to finish
for job_id in "${job_ids[@]}"; do
    wait "$job_id"
done

# Kill the background jobs
for job_id in "${job_ids[@]}"; do
    kill "$job_id"
done

exit 0

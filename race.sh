#!/bin/bash

set -e

# Set the counter to 0
counter=0
echo "{"data": "0"}" > data.json

# Function to send POST request
send_post_request() {
    data="{\"data\": \"$counter\"}"
    result=$(curl -s -X POST -d "$data" -H 'Content-Type: application/json' localhost:8080/write)
    echo "[$(date +%s)] post request result: $result"
}

# Function to send GET request
send_get_request() {
    result=$(curl -s localhost:8080/read)
    echo "[$(date +%s)] get request result: $result"
}

while [ $counter -lt 500 ]; do
    # Run the requests concurrently

    # Run the requests concurrently to test for race conditions
    (
        send_get_request &
        send_post_request &
    )

    # Increment the counter
    ((counter++))
done

exit 0
# Load Tester

This repository contains a load testing script that allows you to test the performance of a web service by sending a specified number of requests per second.

## Code

### Argparse Flags
The argparse flags used in the script are:
- `--qps`: Queries per second (QPS) for the load test.
- `--url`: URL to send HTTP requests.
- `--duration`: Duration of the load test in seconds.
- `--concurrent`: Number of concurrent requests.

### Load Testing Behavior and Explanation
During the load testing process, you may observe certain behaviors or outcomes that are influenced by various factors. Below are explanations for common observations:

#### 1. Fluctuations in Achieved QPS
- **Reason**: The actual queries per second (QPS) achieved during the test may fluctuate due to asynchronous execution, network latency, and server response times.
- **Explanation**: Asynchronous requests and varying response times can impact the rate at which requests are processed, resulting in variations in the achieved QPS compared to the specified value (`--qps`).

#### 2. Latency Variations
- **Reason**: The observed latency for each request may vary based on network conditions, server load, and response times.
- **Explanation**: Network latency, server performance, and concurrency settings influence the latency of individual requests. The reported average latency (`Average Latency`) reflects the overall performance during the test duration.


## Docker

To build and run the Docker container:

1. Ensure you have Docker installed on your machine.
2. Navigate to the directory containing the Dockerfile.
3. Build and run the Docker image using the instructions below:

### Building the Docker Image

Run the following command

```docker build -t <Your-Image-Name> .```

This should build your docker image from Docker file by installing all the required dependencies

### Running the Docker Image

``` 
docker run -it my_load_tester \
--qps <qps-count> \
--duration <duration-sec> \
--url <Input-URL>
 ```

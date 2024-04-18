# Load Tester

This repository contains a load testing script that allows you to test the performance of a web service by sending a specified number of requests per second.

## Code

### Argparse Flags
The argparse flags used in the script are:
- `--qps`: Queries per second (QPS) for the load test.
- `--url`: URL to send HTTP requests.
- `--duration`: Duration of the load test in seconds.
- `--concurrent`: Number of concurrent requests.

## Docker

To build and run the Docker container:

1. Ensure you have Docker installed on your machine.
2. Navigate to the directory containing the Dockerfile.
3. Build the Docker image using the following command:

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

import argparse
import asyncio
import aiohttp
import numpy as np
import matplotlib.pyplot as plt
import time
import statistics
from collections import defaultdict
 
class LoadTester:
    """
    A class for performing load testing on a specified URL.

    Args:
        url (str): The target URL to send HTTP requests.
        qps (float): Queries per second (QPS) for the load test.
        duration (int): Duration of the load test in seconds.
        concurrent_requests (int): Number of concurrent requests to be made.

    Attributes:
        url (str): The target URL to send HTTP requests.
        qps (float): Queries per second (QPS) for the load test.
        duration (int): Duration of the load test in seconds.
        concurrent_requests (int): Number of concurrent requests to be made.
        success_count (int): Number of successful HTTP requests.
        error_count (int): Number of failed HTTP requests.
        latencies (list): List of latencies for successful requests.
        start_time (float): Start time of the load test.
        end_time (float): End time of the load test.
        tasks (set): Set of asyncio tasks for making HTTP requests.
        jobs (set): Set of asyncio tasks for processing finished HTTP requests.
    """
    def __init__(self, url, qps, duration, concurrent_requests):
        self.url = url
        self.qps = qps
        self.duration = duration
        self.concurrent_requests = concurrent_requests
 
        self.success_count = 0
        self.error_count = 0
        self.latencies = []
        self.start_time = None
        self.end_time = None
        self.response_counts = defaultdict(int)
 
        self.tasks = set()
        self.jobs = set()
 
    def _report_partial_metrics(self):
        """
        Report partial metrics during the load test.

        Prints current status including elapsed time, QPS, average latency,
        number of successful requests (200 OK), and number of errors.
        """
        elapsed_time = time.time() - self.start_time
        current_qps = (self.success_count+self.error_count+len(self.tasks))/elapsed_time
        partial_throughput = (self.success_count + self.error_count) / elapsed_time
        print(f"Elapsed Time: {elapsed_time:.2f}s | QPS: {current_qps:.2f}| "
                    f"Latency: {statistics.mean(self.latencies) if len(self.latencies)>0 else 0:.4f}s | "
                    f"200 OK: {self.success_count} | Errors: {self.error_count} | "  
                    f"Partial Throughput: {partial_throughput:.2f} rps")
 
    def _report_full_metrics(self):
        """
        Report full metrics after the load test completes.

        Calculates and prints final metrics including success rate, error rate,
        average latency, minimum latency, and maximum latency.
        """
        total_requests = self.success_count + self.error_count
        error_rate = self.error_count / total_requests if total_requests > 0 else 0
        total_latency = sum(self.latencies)
        latency_ct = len(self.latencies)
        average_latency = total_latency / latency_ct if latency_ct > 0 else 0
        success_rate = self.success_count / total_requests if total_requests > 0 else 0
        elapsed_time = self.end_time - self.start_time
        throughput = total_requests / elapsed_time if elapsed_time > 0 else 0
        latency_p50 =np.quantile(self.latencies, 0.50) if self.latencies else 0
        latency_p95 =np.quantile(self.latencies, 0.95) if self.latencies else 0
        latency_p99 =np.quantile(self.latencies, 0.99) if self.latencies else 0

        print()
        print("Load Test Results".center(50))
        print(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))}".center(50))
        print(f"End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.end_time))}".center(50))
        print(f"Total Number of Requests: {total_requests}".center(50))
        print(f"Success Rate: {success_rate:.2f}".center(50))
        print(f"Error Rate: {error_rate:.2f}".center(50))
        if total_latency > 0:
            print("-" * 50)  # Line separator
            print("Latency Metrics".center(50))
            print(f"Average Latency: {average_latency:.4f}s".center(50))
            print(f"Min Latency: {min(self.latencies):.4f}s".center(50))
            print(f"Max Latency: {max(self.latencies):.4f}s".center(50))
            print(f"Latency P50: {latency_p50:.4f}s".center(50))
            print(f"Latency P95: {latency_p95:.4f}s".center(50))
            print(f"Latency P99: {latency_p99:.4f}s".center(50))
            print(f"Average Throughput: {throughput:.4f} rps".center(50))
        print("-" * 50)  # Line separator
        print("Response Code Counts".center(50))
        for code, count in self.response_counts.items():
            print(f"Response Code {code}: {count}".center(50))
 
    def _plot(self):
        # Show final latency plot
        plt.figure()
        plt.plot(self.latencies)
        plt.xlabel('Request Number')
        plt.ylabel('Latency (seconds)')
        plt.title('Latency per Request')
        plt.savefig('Latency_Request.png')
 
    async def make_request(self, session, url):
        """
        Make an HTTP GET request asynchronously.

        Args:
            session (aiohttp.ClientSession): An aiohttp client session.
            url (str): The URL to make the request to.

        Returns:
            tuple: A tuple containing the HTTP status code and the request latency.
        """
        url_start_time = time.time()
        try:
            async with session.get(url) as response:
                latency = time.time() - url_start_time
                response_code = response.status
                self.response_counts[response_code] += 1
                return response.status, latency
        except aiohttp.ClientError as e:
            response_code = 400  # Set 400 as baseline for client exceptions
            self.response_counts[response_code] +=1
            print(f"Request error: {e}")
            return None, None
 
    async def process_finished_tasks(self, done_tasks):
        """
        Process finished HTTP request tasks.

        Updates success and error counts based on request outcomes.

        Args:
            done_tasks (set): Set of completed asyncio tasks.
        """
        for task in done_tasks:
            status, latency = task.result()
            if status == 200:
                self.success_count += 1
                self.latencies.append(latency)
            else:
                self.error_count += 1
 
            self._report_partial_metrics()
 
    async def run_load_test(self):
        interval = (1*self.concurrent_requests) / self.qps  # Interval between requests in seconds
        current_qps = 0
        self.start_time = time.time()
 
        async with aiohttp.ClientSession() as session:
            # tasks = set()
            request_counter = 0
 
            while time.time() < self.start_time + self.duration:
                current_qps = request_counter / (time.time() - self.start_time + 0.0001)
                n=0
                while n < self.concurrent_requests:
                    task = asyncio.create_task(self.make_request(session, self.url))
                    self.tasks.add(task)
                    task.add_done_callback(self.tasks.discard)
                    request_counter += 1
                    n += 1
 
                # formulas for calculating interval dynamically.
                # interval = (1*self.concurrent_requests)/(2*self.qps - current_qps)
                # interval = ((1*self.concurrent_requests) / self.qps) - 0.00001
 
                interval_start = time.time()
                done, pending = await asyncio.wait(self.tasks, timeout=interval)
                while time.time() - interval_start < interval:
                    pass
 
                self.jobs.add(asyncio.create_task(self.process_finished_tasks(done)))
 
            self.end_time = time.time()
            if len(self.tasks) > 0:
                done, pending = await asyncio.wait(self.tasks, return_when=asyncio.ALL_COMPLETED)
 
            self.jobs.add(asyncio.create_task(self.process_finished_tasks(done)))
 
            if len(self.jobs) > 0:
                done, pending = await asyncio.wait(self.jobs, return_when=asyncio.ALL_COMPLETED)
 
        self._report_full_metrics()
        self._plot()
 
    def start(self):
        asyncio.run(self.run_load_test())
 
# Example usage with command-line arguments
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a load test with specified QPS and concurrent requests.')
    parser.add_argument('--qps', type=float, default=10, help='Queries per second (QPS) for the load test')
    parser.add_argument('--url', type=str, required=True, help='URL to send HTTP requests')
    parser.add_argument('--duration', type=int, default=30, help='Duration of the load test in seconds')
    parser.add_argument('--concurrent', type=int, default=1, help='Number of concurrent requests')
    args = parser.parse_args()
 
    load_tester = LoadTester(args.url, args.qps, args.duration, args.concurrent)
    load_tester.start()
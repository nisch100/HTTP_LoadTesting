# Use the official Python image as the base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the Python script into the container
COPY http_load.py .

# Install any Python dependencies
RUN pip install --upgrade pip && \
    pip install aiohttp matplotlib && \
    pip install requests

# Set the entry point to the Python script
ENTRYPOINT ["python", "http_load.py"]

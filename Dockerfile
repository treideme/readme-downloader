# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY requirements.txt .
COPY fetch_readme.py .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run script when the container launches
ENTRYPOINT ["python", "/usr/src/app/fetch_readme.py"]

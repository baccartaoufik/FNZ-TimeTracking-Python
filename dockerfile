# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Install system dependencies for dlib and mysqlclient
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app
RUN mkdir -p /app/static/images
RUN pip install python-dotenv
# Copy images to the correct directory
COPY static/images/* /app/static/images/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn
# Install dlib separately from source
RUN pip install dlib

ENV FLASK_ENV=production
ENV SECRET_KEY=secret
# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_ENV=production

# Run app.py when the container launches
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]

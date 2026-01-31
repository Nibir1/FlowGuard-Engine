# Use an official Python runtime as a parent image
# Python 3.11.9 is specified in the requirements
FROM python:3.11.9-slim

# Set the working directory in the container
WORKDIR /app

# Prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# Install system dependencies
# gcc and python3-dev are often needed for compiling C extensions (like numpy/pandas if used later)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
# We copy everything so that the 'src' module is resolvable
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the application using Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
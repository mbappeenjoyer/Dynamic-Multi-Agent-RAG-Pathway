# Use the official Python 3.12.3 base image
FROM python:3.12.3-slim

# Set working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install -r requirements.txt

# Copy the application code into the container
COPY . /app/

# Expose the port that Flask will use
EXPOSE 8000

# Command to run the Flask application
CMD ["python", "main.py"]

# Use an official Python runtime as a parent image
FROM python:3.12.1-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /NlchatDjango/

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Daphne with HTTP/2 and TLS support
RUN pip install daphne[twisted] twisted[tls,http2]

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000

# Start the application using Daphne with HTTP/2 support enabled
CMD ["daphne", "-u", "/tmp/daphne.sock", "Nlchat.asgi:application"]
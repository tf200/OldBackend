FROM python:3.12.1-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /healthy

# Install dependencies including GObject libraries
RUN apt-get update && \
    apt-get install -y \
    python3-pip \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    graphviz \
    celery


COPY requirements.txt .

RUN pip3.12 install --no-cache-dir -r requirements.txt

# Install Daphne with HTTP/2 and TLS support
RUN pip3.12 install daphne[twisted] twisted[tls,http2]

# Copy project
COPY . .

# Uncomment if you need to collect static files
# RUN python3.12 manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000

# Start the application using Daphne with HTTP/2 support enabled
CMD ["daphne", "-u", "/tmp/daphne.sock", "healty.asgi:application"]
# Use official Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    gnupg \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm \
    && rm -rf /var/lib/apt/lists/*


# Upgrade pip
RUN pip install --upgrade pip

# Install required Python libraries
# fastmcp is not a well-known PyPI package, so assuming it's installable via pip
RUN pip install fastmcp algoliasearch

# Copy source files
COPY . .

# Expose port if needed (optional, e.g., if it's a web server)
EXPOSE 8080 6277 6274

# Command to run the application
CMD ["fastmcp", "run", "server.py:mcp"]

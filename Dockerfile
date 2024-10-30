# Start with a lightweight Python image
FROM python:3.10-slim

# Install necessary build tools and dependencies for PySNARK
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    swig \
    cmake \
    g++ \
    git \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install PySNARK from GitHub
RUN pip install git+https://github.com/meilof/pysnark

# Set up a working directory in the container
WORKDIR /app

# Copy your local files (replace with your paths)
COPY . /app

# Default command for the container
CMD ["python3"]


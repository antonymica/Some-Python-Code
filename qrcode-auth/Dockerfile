# Use specific version tag for better reproducibility
FROM python:3.13-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create a non-root user to run the application
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory and ensure proper ownership
WORKDIR /app

# Copy and install dependencies as a separate step (for caching)
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files with proper ownership
COPY --chown=appuser:appuser . .

# Make sure our app can't write to its own code but create necessary writable directories
RUN chmod -R 755 /app && \
    find /app -type f -exec chmod 644 {} \; && \
    mkdir -p /app/data /app/instance && \
    chown -R appuser:appuser /app/data /app/instance && \
    chmod -R 755 /app/data /app/instance

# Expose port (though keep in mind exposing is just documentation)
EXPOSE 5000

# Switch to non-root user
USER appuser

# Specify the command to run the application
CMD ["python", "app.py", "--host=0.0.0.0", "--port=5000"]
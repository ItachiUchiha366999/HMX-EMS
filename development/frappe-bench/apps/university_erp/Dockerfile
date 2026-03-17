# University ERP Docker Image
# Built on Frappe/ERPNext base image
#
# NOTE: For development, use the devcontainer setup instead.
# This Dockerfile is for production deployment only.
#
# Development: Use VS Code + Dev Containers with /.devcontainer/
# Production: Use this Dockerfile with docker-compose.yml

ARG FRAPPE_VERSION=version-15
FROM frappe/bench:${FRAPPE_VERSION}

LABEL maintainer="University ERP <support@university.edu>"
LABEL description="Comprehensive University Management System"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

# Switch to root for installations
USER root

# Install additional system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wkhtmltopdf \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    fonts-liberation \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch back to frappe user
USER frappe

# Set working directory
WORKDIR /home/frappe/frappe-bench

# Copy requirements first (for better layer caching)
COPY --chown=frappe:frappe requirements.txt /tmp/university_erp_requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/university_erp_requirements.txt || true

# Copy application code
COPY --chown=frappe:frappe . apps/university_erp

# Install the app
RUN bench get-app file:///home/frappe/frappe-bench/apps/university_erp --skip-assets || true

# Build assets
RUN bench build --app university_erp

# Expose ports
EXPOSE 8000 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/method/frappe.ping || exit 1

# Default command
CMD ["bench", "start"]

FROM python:3.12-slim

WORKDIR /app
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m -u 1000 brain && chown brain:brain /app

# Copy only the server folder to preserve absolute imports (server.app)
COPY server/ /app/server/
COPY .env /app/.env

# Ensure data directory exists and is writable
RUN mkdir -p /app/data && chown -R brain:brain /app

USER brain

EXPOSE 8000
# Use the package path for uvicorn
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]

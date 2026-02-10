FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m -u 1000 brain && chown brain:brain /app

# Copy all server files
COPY . .

# Ensure data directory exists and is writable
RUN mkdir -p /app/data && chown -R brain:brain /app

USER brain

EXPOSE 8000
# Run through main:app to match common conventions
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

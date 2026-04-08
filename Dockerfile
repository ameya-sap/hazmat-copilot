FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy only pyproject.toml to cache dependencies (bypassing uv.lock due to private registry issues)
COPY pyproject.toml ./

# Sync dependencies (this creates .venv) using public PyPI
RUN uv sync --index-url https://pypi.org/simple

# Copy the rest of the app
COPY . .

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run the server using the venv python
CMD [".venv/bin/python", "app/server.py"]

FROM python:3.13-slim

# Install uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy pyproject.toml and README.md for dependency resolution
COPY pyproject.toml README.md ./

# Install dependencies using uv
RUN uv pip install --system -e .

# Copy the rest of the application code
COPY . .

# Set environment variables for production
ENV MCP_TRANSPORT=streamable-http
ENV PORT=8080

# Expose port for Cloud Run
EXPOSE 8080

# Run the application using uv
CMD ["uv", "run", "python", "main.py"]

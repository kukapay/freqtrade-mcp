FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir --root-user-action=ignore freqtrade-client>=2025.2 "mcp[cli]>=1.5.0"

# Copy application file
COPY __main__.py ./

# Set environment variables (can be overridden at runtime)
ENV FREQTRADE_API_URL=http://freqtrade:8080
ENV FREQTRADE_USERNAME=Freqtrader
ENV FREQTRADE_PASSWORD=SuperSecret1!
ENV PYTHONUNBUFFERED=1

# Run the MCP server
CMD ["python", "-u", "__main__.py"]
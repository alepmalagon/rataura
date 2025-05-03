FROM python:3.10-slim

WORKDIR /app

# Copy the eve_wiggin package
COPY eve_wiggin /app/eve_wiggin

# Install the eve_wiggin package
WORKDIR /app
RUN pip install -e ./eve_wiggin

# Expose port for web application
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the web application by default
CMD ["python", "-m", "eve_wiggin.web"]

# Alternatively, you can run the CLI version with:
# CMD ["python", "-m", "eve_wiggin"]


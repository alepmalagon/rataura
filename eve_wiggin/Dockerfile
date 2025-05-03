FROM python:3.10-slim

WORKDIR /app

# Copy the eve_wiggin package
COPY eve_wiggin /app/eve_wiggin

# Install the eve_wiggin package
WORKDIR /app
RUN pip install -e ./eve_wiggin

# Run the application
CMD ["python", "-m", "eve_wiggin"]

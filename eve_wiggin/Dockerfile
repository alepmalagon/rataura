FROM python:3.10-slim

WORKDIR /app

# Copy the parent rataura package first
COPY rataura /app/rataura
COPY setup.py /app/
COPY requirements.txt /app/
COPY README.md /app/

# Install the rataura package
RUN pip install -e .

# Copy the eve_wiggin package
COPY eve_wiggin /app/eve_wiggin

# Install the eve_wiggin package
WORKDIR /app/eve_wiggin
RUN pip install -e .

# Run the application
CMD ["python", "-m", "eve_wiggin"]

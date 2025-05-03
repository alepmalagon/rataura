FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY eve_wiggin/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire repository
COPY . .

# Install both packages
RUN pip install -e ./rataura
RUN pip install -e ./eve_wiggin

# Run the application
CMD ["python", "-m", "eve_wiggin"]

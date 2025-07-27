# Use a lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /backend/app

# Copy the requirements.txt file from the backend folder
COPY requirements.txt .

# Install Python dependencies
RUN python -m venv /opt/venv \
 && . /opt/venv/bin/activate \
 && pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy the backend source code into the container
COPY backend/ ./backend/

# Expose the FastAPI port
EXPOSE 8000

# Run the FastAPI app using Uvicorn
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]


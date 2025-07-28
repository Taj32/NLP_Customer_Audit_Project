# Use a lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file from the backend folder
COPY backend/requirements.txt .

# Install Python dependencies
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the backend source code into the container
COPY backend/ ./backend/

# Expose the FastAPI port
EXPOSE 8000

# Ensure the virtual environment is used for the CMD
ENV PATH="/opt/venv/bin:$PATH"

# Run the FastAPI app using Uvicorn
CMD ["/opt/venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

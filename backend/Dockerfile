# FROM python:3.12-slim

# # Set working directory
# WORKDIR /app

# # Install system dependencies needed for PyAudio and other packages
# RUN apt-get update && apt-get install -y \
#     gcc \
#     libasound2-dev \
#     portaudio19-dev \
#     libportaudio2 \
#     libportaudiocpp0 \
#     ffmpeg \
#     && rm -rf /var/lib/apt/lists/*

# # Copy backend requirements and install Python dependencies
# COPY requirements.txt .
# RUN pip install --upgrade pip
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy backend source code
# COPY . .

# # Expose the FastAPI port
# EXPOSE 8000

# # Run the FastAPI app
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.12-slim

WORKDIR /app

# Copy only the FastAPI backend code
COPY requirements.txt .

RUN python -m venv /opt/venv \
 && . /opt/venv/bin/activate \
 && pip install --upgrade pip \
 && pip install -r requirements.txt

COPY app/ ./app/

CMD ["/opt/venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


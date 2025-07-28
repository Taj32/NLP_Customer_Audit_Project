# # Use a lightweight Python image
# FROM python:3.12-slim

# # Set the working directory inside the container to /backend
# WORKDIR /backend

# # Debug: Print the current working directory
# RUN echo "Current working directory:" && pwd

# # Copy the requirements.txt file from the backend folder
# COPY requirements.txt .

# # Debug: Print the contents of the current directory after copying requirements.txt
# RUN echo "Contents of /backend after copying requirements.txt:" && ls -la

# # Install Python dependencies
# RUN python -m venv /opt/venv \
#  && /opt/venv/bin/pip install --upgrade pip \
#  && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# # Debug: Print installed Python packages
# RUN echo "Installed Python packages:" && /opt/venv/bin/pip list

# # Copy the entire backend folder into the container
# COPY backend/ .

# # Debug: Print the contents of the /backend directory after copying the backend folder
# RUN echo "Contents of /backend after copying backend folder:" && ls -la

# # Expose the FastAPI port
# EXPOSE 8000

# # Ensure the virtual environment is used for the CMD
# ENV PATH="/opt/venv/bin:$PATH"

# # Debug: Print the PATH environment variable
# RUN echo "PATH environment variable:" && echo $PATH

# # Run the FastAPI app using Uvicorn
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


# Use a lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container to /backend
WORKDIR /backend

# Copy only the FastAPI backend code (requirements + app + create_db.py)
COPY requirements.txt .
COPY app/ ./app
#COPY create_db.py .  # optional — only if needed at runtime

# Install Python dependencies inside a virtual environment
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Expose the FastAPI port
EXPOSE 8000

# Use the virtual environment's path
ENV PATH="/opt/venv/bin:$PATH"

# Run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


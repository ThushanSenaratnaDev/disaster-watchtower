# 1. Start with a lightweight Python image
FROM python:3.11-slim

# 2. Setting the working directory inside the container
# This is where all commands will run by default
WORKDIR /app

# 3. Copy only the requirements file first
# Docker caches layers. If requirements.txt doesn't change, 
# Docker won't re-run the pip install step (saves time).
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the code
COPY . .

# 6. Default command (optional, we will override this later)
CMD ["python", "scripts/fetch_earthquakes.py"]
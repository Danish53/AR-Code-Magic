# Base image: Node.js + Debian-based system (for Blender support)
FROM node:20-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies required for Blender
RUN apt-get update && apt-get install -y --no-install-recommends \
    blender \
    xvfb \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy project files
COPY . .

# Expose port (if your app runs on port 8000)
EXPOSE 8000

# Default command to run the app
CMD ["npm", "run", "dev"]

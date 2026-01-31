# Stage 1: Dev (Vite runs in container)
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files first (for Docker layer caching)
COPY package.json package-lock.json* ./

# Install dependencies inside the container
RUN npm install

# Copy the rest of the frontend source
COPY . .

# Vite dev server port
EXPOSE 5173

# Run Vite in dev mode, accessible from outside container
CMD ["npm", "run", "dev", "--", "--host"]

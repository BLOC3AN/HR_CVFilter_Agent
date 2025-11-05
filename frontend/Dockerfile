# Frontend UI Service Dockerfile - Vite + React
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source code
COPY frontend/ ./

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8501/ || exit 1

# Run nginx
CMD ["nginx", "-g", "daemon off;"]


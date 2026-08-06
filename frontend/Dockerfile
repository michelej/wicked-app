FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN pnpm install

# Copy application files
COPY . .

# Expose port
EXPOSE 5173

# Run the application
CMD ["pnpm", "run", "dev"]

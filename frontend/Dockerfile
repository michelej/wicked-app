FROM node:20-alpine

WORKDIR /app

# Enable pnpm via Corepack
RUN corepack enable

# Copy package files
COPY package.json pnpm-lock.yaml .npmrc ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy application files
COPY . .

# Expose port
EXPOSE 5173

# Run the application
CMD ["pnpm", "run", "dev"]

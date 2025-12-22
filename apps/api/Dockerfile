FROM oven/bun:1.1.0-alpine
WORKDIR /app

# Copy all files for monorepo context (could be optimized)
COPY . .

# Install dependencies
RUN bun install

# Go to api directory
WORKDIR /app/apps/api

EXPOSE 3000
CMD ["bun", "run", "dev"]

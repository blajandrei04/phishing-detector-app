# Stage 1: Build the Angular application
FROM node:22-alpine AS build

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy source code and build
COPY . .
RUN npm run build -- --configuration production

# Stage 2: Serve the application using Node (SSR)
FROM node:22-alpine

WORKDIR /app

# Copy the built output from the build stage
COPY --from=build /app/dist /app/dist
COPY --from=build /app/package*.json ./

# Expose port 4000 (Angular SSR default)
EXPOSE 4000

# Set Node environment to production
ENV NODE_ENV=production

# Start the SSR server
CMD ["node", "dist/frontend/server/server.mjs"]

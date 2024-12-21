# Use a minimal image for development
FROM node:18-alpine

# Set working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock) into the container
COPY package.json package-lock.json* ./

# Install the app dependencies with --legacy-peer-deps to bypass the peer dependency conflict
RUN npm install --legacy-peer-deps

# Copy the rest of the application files into the container
COPY . .

# Expose the port the app will run on
EXPOSE 3000

# Start the Next.js app in development mode
CMD ["npm", "run", "dev"]

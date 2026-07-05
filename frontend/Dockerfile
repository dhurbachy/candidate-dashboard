# Use an official Node.js runtime as a base image
FROM node:20-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package manifests first to leverage Docker caching layers
COPY package*.json ./

# Install frontend dependencies
RUN npm install

# Copy all your frontend project source files
COPY . .

# Expose the default Vite server port
EXPOSE 5173

# Run the development server bound to all network interfaces
CMD ["npm", "run", "dev", "--", "--host"]

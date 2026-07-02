FROM node:20-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
EXPOSE 8081
ENV EXPO_PUBLIC_API_URL=https://trade-iq-deploy.onrender.com
CMD ["npx", "expo", "start", "--web", "--port", "8081", "--non-interactive"]

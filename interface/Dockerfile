FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm install

COPY . .

ARG NEXT_PUBLIC_API_URL=flask:5001
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Construire l'application Next.js
RUN npm run build

# Exposer le port sur lequel l'application va tourner
EXPOSE 3000

# Commande pour démarrer l'application
CMD ["npm", "start"]

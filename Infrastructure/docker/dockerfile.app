FROM node:18-alpine

WORKDIR /app

COPY app /app

RUN yarn install
FROM oven/bun:1.1.0-alpine as builder
WORKDIR /app
COPY . .
RUN bun install
WORKDIR /app/apps/web
RUN bun run build

FROM nginx:alpine
COPY --from=builder /app/apps/web/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

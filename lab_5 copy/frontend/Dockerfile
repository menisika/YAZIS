# ══════════════════════════════════════════════════════════════════════════════
# Stage 1 — deps
#   Installs node_modules once; cached until package-lock.json changes.
# ══════════════════════════════════════════════════════════════════════════════
FROM node:22-alpine AS deps

WORKDIR /app

# Copy only manifest files first so the npm ci layer is cached independently
# of source-code changes.
COPY package.json package-lock.json ./

# Use `npm install` (not `npm ci`) so the lockfile can self-heal when it drifts
# slightly from package.json — acceptable for a dev image.
RUN npm install --no-audit --no-fund


# ══════════════════════════════════════════════════════════════════════════════
# Stage 2 — dev
#   Runs the Vite dev server with HMR. src/ is bind-mounted by docker-compose,
#   so code changes on the host are reflected live inside the container.
# ══════════════════════════════════════════════════════════════════════════════
FROM node:22-alpine AS dev

WORKDIR /app

ENV NODE_ENV=development \
    CHOKIDAR_USEPOLLING=true

# Reuse the pre-built node_modules from the deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy the rest of the project (overridden by the src/ volume mount in compose)
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

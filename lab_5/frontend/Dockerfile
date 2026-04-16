# ══════════════════════════════════════════════════════════════════════════════
# Stage 1 — dependency installer
#   Installs node_modules in isolation so this layer is cached independently
#   of source-code changes.  Rebuilds only when package-lock.json changes.
#
#   node:23-alpine ships npm 11 which matches the lock-file format generated
#   by the local npm 11 install; node:22-alpine's npm 10 would reject it.
# ══════════════════════════════════════════════════════════════════════════════
FROM node:23-alpine AS deps

WORKDIR /app

# Copy only the lockfiles first – maximises Docker layer cache hit rate
COPY package.json package-lock.json ./

# Reproducible install from the lockfile (no stray version changes)
RUN npm ci


# ══════════════════════════════════════════════════════════════════════════════
# Stage 2 — development server
#   Receives the pre-built node_modules from Stage 1.
#   In development the `src/` directory is volume-mounted from the host,
#   so Vite's HMR picks up edits instantly without rebuilding this image.
# ══════════════════════════════════════════════════════════════════════════════
FROM node:23-alpine AS dev

WORKDIR /app

# Bring in the installed modules (no re-download needed)
COPY --from=deps /app/node_modules ./node_modules

# Copy everything except src/ and node_modules (see .dockerignore).
# Vite needs index.html, vite.config.ts, tsconfig*.json, public/, etc.
# src/ will be overridden by the volume mount at runtime.
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Stage 1: Build
FROM node:20-alpine AS build

WORKDIR /app

# We will populate these in Phase 5. 
# For now, this Dockerfile assumes standard React/Vite structure.
# If files don't exist yet, Docker build might fail, but this is the target state.
# NOTE: This file is kept simple for dev mode in this phase.

CMD ["npm", "run", "dev", "--", "--host"]
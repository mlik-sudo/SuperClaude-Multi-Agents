# ===================================
# SuperClaude Multi-Agents - Dockerfile
# ===================================
# Build stage for optimized image

FROM python:3.9-slim as builder

# Métadonnées
LABEL maintainer="SuperClaude Team"
LABEL description="SuperClaude Multi-Agents orchestrator"
LABEL version="1.0.0"

# Variables d'environnement pour Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Créer un répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances dans un venv
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -r requirements.txt

# ===================================
# Production stage
# ===================================
FROM python:3.9-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Installer les dépendances système nécessaires
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tini \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 -s /bin/bash superclaude && \
    mkdir -p /app /app/.ai /app/logs /app/data && \
    chown -R superclaude:superclaude /app

# Répertoire de travail
WORKDIR /app

# Copier le venv depuis le builder
COPY --from=builder /opt/venv /opt/venv

# Copier le code source
COPY --chown=superclaude:superclaude . .

# Rendre le CLI exécutable
RUN chmod +x ai && \
    chmod +x setup.sh

# Passer à l'utilisateur non-root
USER superclaude

# Créer le fichier .env s'il n'existe pas (depuis .env.example)
RUN if [ ! -f .env ]; then cp .env.example .env; fi

# Volumes pour la persistance
VOLUME ["/app/.ai", "/app/logs", "/app/data"]

# Port pour les futurs services (optionnel)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from cli.ai.main import AICli; import sys; sys.exit(0)" || exit 1

# Point d'entrée avec tini pour gérer les signaux
ENTRYPOINT ["/usr/bin/tini", "--"]

# Commande par défaut
CMD ["./ai", "status"]

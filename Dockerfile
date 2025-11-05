# Usar Python 3.12 como imagem base
FROM python:3.12-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias para psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de configuração e dependências
COPY pyproject.toml uv.lock ./

# Instalar uv (gerenciador de pacotes rápido)
RUN pip install uv

# Instalar dependências usando uv
RUN uv sync --frozen --no-install-project

# Copiar código fonte
COPY bot.py main.py ./

# Criar diretório para logs/arquivos
RUN mkdir -p /app/data

# Definir variável de ambiente para Python
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Comando padrão para executar o bot
CMD ["uv", "run", "python", "bot.py"]
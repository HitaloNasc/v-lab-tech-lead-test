# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Variáveis de ambiente para não gerar .pyc e buffer de logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Exemplo: define variáveis de ambiente padrão (pode ser sobrescrito)
ENV APP_ENV=prod

# Porta padrão do Uvicorn
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

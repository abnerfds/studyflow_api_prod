# 1. Usamos uma imagem leve do Python 3.11
FROM python:3.11-slim

# 2. Define onde as coisas vão acontecer dentro do container
WORKDIR /app

# 3. Evita que o Python gere arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 4. Instala dependências do sistema necessárias para o driver do Postgres (asyncpg/psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copia e instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copia todo o código do seu projeto para dentro do container
COPY . .

# 7. Informa que a porta 8000 será usada
EXPOSE 8000

# 8. Comando para iniciar a API (ajuste 'main:app' se o seu arquivo principal tiver outro nome)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
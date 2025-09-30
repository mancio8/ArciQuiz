# Usa immagine Python ufficiale
FROM python:3.11-slim

# Imposta directory di lavoro
WORKDIR /app

# Copia requirements (crea requirements.txt con Django e psycopg2-binary)
COPY requirements.txt /app/

# Installa dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il progetto
COPY . /app/

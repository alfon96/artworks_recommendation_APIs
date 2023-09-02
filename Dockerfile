# Usa l'immagine ufficiale di Python 3.9.4 come base
FROM python:3.9.4

# Imposta il working directory
WORKDIR /app

# Copia il file requirements.txt nella directory /app
COPY requirements.txt .

# Installa i pacchetti richiesti
RUN pip install --no-cache-dir -r requirements.txt

# Copia l'intera app nella directory /app
COPY . .

# Installa font per i grafici
RUN apt-get update && \
    apt-get install -y fontconfig

RUN mkdir -p /usr/share/fonts/truetype/custom
COPY /app/file_statici/fonts/PoppinsLight.ttf /usr/share/fonts/truetype/custom/

RUN fc-cache -f -v

ENV debug=false

# Define the PORT environment variable

# Esposizione della porta 80 per la comunicazione del server
EXPOSE 80

# Avvia il server Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

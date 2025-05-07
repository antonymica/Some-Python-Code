FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
RUN mkdir -p /app/data
# Exposer le port
EXPOSE 5000
# Lancer le serveur avec gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
